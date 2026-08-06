#!/usr/bin/env python3
"""Health watchdog for rosbridge_websocket, independent of the dynamic bridge's own watchdog.

**Why this exists.** `rosbridge-websocket.service` has `Restart=always`, but the failure this
guards against never kills the process: rosbridge stays `active` and stops *serving*. It has
happened twice in one day (05.08.2026) under browser-session churn — new connections time out
during the opening handshake while the log repeats `WebSocketClosedError` once a second. The
second time it took down the backend's own command channel as well, so the robot could not be
commanded at all. Unattended, during EXP-09's 72 h soak, that ends the patrol *and* the ability
to stop it from the console. systemd cannot see any of it, so something has to ask.

**Why not fix it at the source.** rosbridge_server here is 1.3.1 (Foxy), which exposes no
`websocket_ping_*` parameters — only `unregister_timeout` — so there is no dead-peer detection to
enable. The gateway already releases a departed browser's subscriptions (P1.5/D-13) and the fault
recurred anyway. A supervised restart is the lever that exists.

**Two probes, because there are two ways to be dead.**

* Probe A (handshake, frequent) opens a websocket, completes the handshake and closes cleanly.
  This is the exact signature that was observed: `TimeoutError: timed out during opening
  handshake`. It subscribes to nothing, so it is the cheapest question that distinguishes
  "rosbridge is serving" from "something is listening on 9090".
* Probe B (round trip, occasional) subscribes to odometry, requires a real message, then
  unsubscribes and closes. It catches the other failure — connections accepted while no data
  flows — which a handshake alone would call healthy.

**This process sources no ROS environment at all.** That is deliberate, not incidental. Both
health checks in `ros1_dynamic_bridge_watchdog.sh` were once blinded by having noetic and foxy
sourced together, one of them for months; a probe that speaks plain websockets to a TCP port
cannot repeat that mistake. Tornado is already installed as a rosbridge dependency, so this adds
no package to the frozen baseline either.

**Restarting is safe for both clients, verified in their code rather than assumed.** The console's
telemetry client (`frontend/src/telemetry/rosClient.js`) reconnects with backoff and re-subscribes
on connect; the backend's command channel (`backend/app/ros.py`) reconnects and, on reconnect,
**re-asserts a latched emergency stop before re-subscribing**. A robot stopped by an operator
therefore stays stopped across a restart performed here.

**Restraint is part of the design.** A watchdog that restarts eagerly is how the dynamic bridge's
restart counter once reached five figures. Hence: consecutive failures only, a floor on how often
a restart may happen, and suppression while the dynamic bridge is itself restarting — its restarts
destroy the ROS 2 publishers rosbridge has matched, so rosbridge failing in that window is
expected, not its own fault.

**The log is measurement data, not convenience.** Every event goes to journald and to
`/var/log/robco/rosbridge_health.jsonl`, one complete JSON object per line, including the
recovery latency after a restart. EXP-09 reads that file: it turns "rosbridge wedged twice today
and a restart fixed it" into detection latency, recovery latency and event count over 72 hours —
Г5 fault-matrix data about the availability of the mediated command path.
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from tornado.httpclient import HTTPRequest
from tornado.websocket import websocket_connect

# --- configuration ---------------------------------------------------------------------------
# Environment overrides exist so the unit file can document the values it runs with, and so a
# test run can be made impatient without editing this file.

#: rosbridge is reached on the loopback: this runs on the bridge host, and :9090 is firewalled to
#: the web VM alone. The probe therefore tests rosbridge, not the firewall.
URL = os.environ.get("ROSBRIDGE_URL", "ws://127.0.0.1:9090")

PROBE_A_INTERVAL = float(os.environ.get("PROBE_A_INTERVAL", "15"))
PROBE_A_TIMEOUT = float(os.environ.get("PROBE_A_TIMEOUT", "5"))
PROBE_A_FAILURES = int(os.environ.get("PROBE_A_FAILURES", "3"))

PROBE_B_INTERVAL = float(os.environ.get("PROBE_B_INTERVAL", "300"))
PROBE_B_TIMEOUT = float(os.environ.get("PROBE_B_TIMEOUT", "10"))
PROBE_B_FAILURES = int(os.environ.get("PROBE_B_FAILURES", "2"))

#: Odometry: the highest-rate topic that is always published while the simulation runs, so a
#: missing message inside the timeout means the read path is down rather than merely quiet.
PROBE_B_TOPIC = os.environ.get("PROBE_B_TOPIC", "/robot/robotnik_base_control/odom")
PROBE_B_TYPE = os.environ.get("PROBE_B_TYPE", "nav_msgs/msg/Odometry")

UNIT = os.environ.get("ROSBRIDGE_UNIT", "rosbridge-websocket")
GUARD_UNIT = os.environ.get("GUARD_UNIT", "ros1-dynamic-bridge")

#: The floor between restarts **when the previous one did not work**. Restarting in a loop a
#: service that restarting does not fix helps nobody and destroys the evidence.
#:
#: It deliberately does NOT apply to a fault that recurs after a genuine recovery. On 06.08.2026
#: rosbridge wedged, was restarted, served normally for four and a half minutes, and wedged again —
#: and this floor then held the second restart back for five minutes while a regression suite ran
#: against a dead read path. That is not thrashing; that is the fault happening twice, and the
#: second one deserves the same fast answer as the first.
MIN_RESTART_INTERVAL = float(os.environ.get("MIN_RESTART_INTERVAL", "600"))

#: The floor that applies even to a fresh fault, so a service failing every few seconds still
#: cannot be restarted in a tight loop.
MIN_RESTART_INTERVAL_AFTER_RECOVERY = float(
    os.environ.get("MIN_RESTART_INTERVAL_AFTER_RECOVERY", "60")
)
#: Do not restart rosbridge within this long of the dynamic bridge having restarted.
GUARD_WINDOW = float(os.environ.get("GUARD_WINDOW", "60"))
#: How long to keep asking after a restart before calling the recovery failed.
RECOVERY_TIMEOUT = float(os.environ.get("RECOVERY_TIMEOUT", "120"))
RECOVERY_POLL = float(os.environ.get("RECOVERY_POLL", "5"))

#: A summary line at this cadence, so a quiet 72 h run still proves the watchdog was alive.
SUMMARY_INTERVAL = float(os.environ.get("SUMMARY_INTERVAL", "600"))

LOG_PATH = Path(os.environ.get("HEALTH_LOG", "/var/log/robco/rosbridge_health.jsonl"))
LOG_MAX_BYTES = int(os.environ.get("HEALTH_LOG_MAX_BYTES", str(32 * 1024 * 1024)))

TICK = 1.0

_running = True


def _stop(signum, _frame) -> None:
    global _running
    _running = False
    print(f"received signal {signum}, stopping", flush=True)


def record(event: str, **fields) -> None:
    """Write one event to journald and to the JSONL log.

    Logging failures never become watchdog failures: a watchdog that dies because a disk filled
    up is worse than one that keeps supervising without a record.
    """
    entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "event": event}
    entry.update(fields)
    line = json.dumps(entry, ensure_ascii=False)
    print(line, flush=True)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > LOG_MAX_BYTES:
            LOG_PATH.replace(LOG_PATH.with_suffix(LOG_PATH.suffix + ".1"))
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except Exception as exc:  # noqa: BLE001 - see docstring
        print(f"health log unwritable: {type(exc).__name__}: {exc}", flush=True)


# --- the probes ------------------------------------------------------------------------------


async def _probe_handshake() -> str:
    """Complete a websocket handshake and close cleanly.

    Closing cleanly matters: this connects every 15 s, and the fault being watched for is
    associated with connection churn. A probe that left sockets for rosbridge to reap would be
    contributing to what it measures.
    """
    # Only `connect_timeout` is set. Tornado's `request_timeout` would also abort an *established*
    # websocket when it expires, which is wrong for a probe that measures the handshake; the
    # caller bounds the whole probe anyway.
    connection = await websocket_connect(HTTPRequest(URL, connect_timeout=PROBE_A_TIMEOUT))
    connection.close()
    return "handshake accepted"


async def _probe_round_trip() -> str:
    """Subscribe, require one real message, unsubscribe, close.

    `throttle_rate` and `queue_length` keep this to a single message rather than opening a 33 Hz
    firehose for two seconds; the unsubscribe is sent even when the wait fails, because a probe
    that leaks subscriptions upstream is the fault it is looking for.
    """
    connection = await websocket_connect(HTTPRequest(URL, connect_timeout=PROBE_B_TIMEOUT))
    try:
        await connection.write_message(
            json.dumps(
                {
                    "op": "subscribe",
                    "topic": PROBE_B_TOPIC,
                    "type": PROBE_B_TYPE,
                    "throttle_rate": 1000,
                    "queue_length": 1,
                }
            )
        )
        deadline = time.monotonic() + PROBE_B_TIMEOUT
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"no message on {PROBE_B_TOPIC} within {PROBE_B_TIMEOUT:g}s")
            raw = await asyncio.wait_for(connection.read_message(), timeout=remaining)
            if raw is None:
                raise ConnectionError("rosbridge closed the connection")
            message = json.loads(raw)
            if message.get("op") == "publish" and message.get("topic") == PROBE_B_TOPIC:
                return f"message received on {PROBE_B_TOPIC}"
    finally:
        try:
            await connection.write_message(
                json.dumps({"op": "unsubscribe", "topic": PROBE_B_TOPIC})
            )
        except Exception:  # noqa: BLE001 - the connection is going away regardless
            pass
        connection.close()


def run_probe(loop: asyncio.AbstractEventLoop, coro_factory, timeout: float):
    """Run one probe to completion. Returns (ok, detail)."""
    try:
        detail = loop.run_until_complete(asyncio.wait_for(coro_factory(), timeout=timeout + 2))
        return True, detail
    except Exception as exc:  # noqa: BLE001 - every failure is a failed probe, and we say why
        return False, f"{type(exc).__name__}: {exc}"


# --- systemd interaction ---------------------------------------------------------------------


def guard_unit_age() -> float | None:
    """Seconds since `GUARD_UNIT` last entered active, or None if unknown."""
    try:
        output = subprocess.check_output(
            ["systemctl", "show", GUARD_UNIT, "-p", "ActiveEnterTimestampMonotonic"],
            text=True,
            timeout=10,
        )
        value = int(output.strip().split("=", 1)[1])
    except Exception:  # noqa: BLE001 - an unknown guard state must not block a restart
        return None
    if value == 0:
        return None
    return time.clock_gettime(time.CLOCK_MONOTONIC) - value / 1e6


def restart_unit() -> tuple[bool, str]:
    try:
        subprocess.run(
            ["systemctl", "restart", UNIT], check=True, timeout=90, capture_output=True, text=True
        )
        return True, "restarted"
    except subprocess.CalledProcessError as exc:
        return False, f"systemctl exited {exc.returncode}: {(exc.stderr or '').strip()[:200]}"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


# --- main loop -------------------------------------------------------------------------------


def main() -> int:
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    record(
        "started",
        url=URL,
        unit=UNIT,
        probe_a={"interval_s": PROBE_A_INTERVAL, "failures_to_act": PROBE_A_FAILURES},
        probe_b={
            "interval_s": PROBE_B_INTERVAL,
            "failures_to_act": PROBE_B_FAILURES,
            "topic": PROBE_B_TOPIC,
        },
        min_restart_interval_s=MIN_RESTART_INTERVAL,
    )

    now = time.monotonic()
    next_a, next_b, next_summary = now, now + PROBE_B_INTERVAL, now + SUMMARY_INTERVAL
    consecutive = {"A": 0, "B": 0}
    counts = {"A_run": 0, "A_fail": 0, "B_run": 0, "B_fail": 0}
    restarts = 0
    last_restart = None  # monotonic seconds
    # Whether the service has actually served since the last restart. It decides which floor
    # applies: a fault that recurs after a real recovery is a new fault, not a restart loop.
    served_since_restart = True

    while _running:
        now = time.monotonic()
        trigger = None
        last_detail = ""

        if now >= next_a:
            next_a = now + PROBE_A_INTERVAL
            counts["A_run"] += 1
            ok, detail = run_probe(loop, _probe_handshake, PROBE_A_TIMEOUT)
            if ok:
                if consecutive["A"]:
                    record("probe_recovered", probe="A", after_failures=consecutive["A"])
                consecutive["A"] = 0
                served_since_restart = True
            else:
                counts["A_fail"] += 1
                consecutive["A"] += 1
                last_detail = detail
                record("probe_failure", probe="A", consecutive=consecutive["A"], detail=detail)
                if consecutive["A"] >= PROBE_A_FAILURES:
                    trigger = "A"

        if _running and now >= next_b:
            next_b = now + PROBE_B_INTERVAL
            counts["B_run"] += 1
            ok, detail = run_probe(loop, _probe_round_trip, PROBE_B_TIMEOUT)
            if ok:
                if consecutive["B"]:
                    record("probe_recovered", probe="B", after_failures=consecutive["B"])
                consecutive["B"] = 0
            else:
                counts["B_fail"] += 1
                consecutive["B"] += 1
                last_detail = detail
                record("probe_failure", probe="B", consecutive=consecutive["B"], detail=detail)
                if consecutive["B"] >= PROBE_B_FAILURES:
                    trigger = trigger or "B"

        if trigger:
            guard_age = guard_unit_age()
            since_restart = None if last_restart is None else time.monotonic() - last_restart
            if guard_age is not None and guard_age < GUARD_WINDOW:
                # The dynamic bridge just restarted; its restarts destroy the ROS 2 publishers
                # rosbridge matched, so this failure is downstream of that, not rosbridge's own.
                record(
                    "restart_suppressed",
                    reason="guard_unit_recently_restarted",
                    probe=trigger,
                    guard_unit=GUARD_UNIT,
                    guard_age_s=round(guard_age, 1),
                )
                consecutive[trigger] = 0
            elif since_restart is not None and since_restart < (
                MIN_RESTART_INTERVAL_AFTER_RECOVERY if served_since_restart
                else MIN_RESTART_INTERVAL
            ):
                # Two floors, and which one applies is the whole point. If the service served
                # normally since the last restart, this is the fault happening again and it gets
                # the short floor. If it never served, restarting plainly is not the answer and the
                # long floor holds — that is the restart loop worth preventing.
                record(
                    "restart_suppressed",
                    reason="min_interval_after_recovery" if served_since_restart
                    else "min_interval_without_recovery",
                    probe=trigger,
                    since_last_restart_s=round(since_restart, 1),
                    served_since_restart=served_since_restart,
                    min_restart_interval_s=(
                        MIN_RESTART_INTERVAL_AFTER_RECOVERY if served_since_restart
                        else MIN_RESTART_INTERVAL
                    ),
                )
            else:
                record(
                    "restarting",
                    probe=trigger,
                    consecutive=consecutive[trigger],
                    detail=last_detail,
                    unit=UNIT,
                )
                started = time.monotonic()
                ok, detail = restart_unit()
                # The floor applies to *attempts*, so a restart that cannot be performed at all
                # does not turn into a retry loop. The counter, which EXP-09 reports, counts only
                # restarts that actually happened.
                last_restart = time.monotonic()
                # Not served *yet*: the recovery probe below is what earns this back, and until it
                # does, the long floor is the one that applies.
                served_since_restart = False
                if not ok:
                    record("restart_failed", detail=detail, unit=UNIT)
                else:
                    restarts += 1
                    # Recovery is measured, not assumed: keep asking until the handshake is
                    # accepted again. This latency is what EXP-09 reports as time-to-recovery.
                    deadline = time.monotonic() + RECOVERY_TIMEOUT
                    recovered = False
                    probe_detail = "not probed"
                    while _running and time.monotonic() < deadline:
                        time.sleep(RECOVERY_POLL)
                        probe_ok, probe_detail = run_probe(
                            loop, _probe_handshake, PROBE_A_TIMEOUT
                        )
                        if probe_ok:
                            recovered = True
                            # It served: a later fault is a new fault, and gets the short floor.
                            served_since_restart = True
                            record(
                                "recovered",
                                latency_s=round(time.monotonic() - started, 2),
                                restarts_total=restarts,
                            )
                            break
                    if not recovered:
                        record(
                            "recovery_failed",
                            waited_s=round(time.monotonic() - started, 1),
                            detail=probe_detail,
                        )
                consecutive["A"] = consecutive["B"] = 0
                next_a = time.monotonic() + PROBE_A_INTERVAL
                next_b = time.monotonic() + PROBE_B_INTERVAL

        if _running and time.monotonic() >= next_summary:
            next_summary = time.monotonic() + SUMMARY_INTERVAL
            record("summary", restarts_total=restarts, **counts)
            counts = {"A_run": 0, "A_fail": 0, "B_run": 0, "B_fail": 0}

        if _running:
            time.sleep(TICK)

    record("stopped", restarts_total=restarts)
    loop.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
