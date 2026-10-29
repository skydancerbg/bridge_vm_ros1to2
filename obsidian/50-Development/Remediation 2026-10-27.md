# Remediation 2026-10-27 (mirror of phd_experiments/code_review_2026-10-27)

# HANDOFF — remediation of the 27.10.2026 code review (read this first in a new session)

**Last update:** 29.10.2026 12:39 — 1.1-1.10, 2.5a, 2.5, 2.6, 2.7 merged; next 2.1

This file lets a new Claude session (or the owner) continue the remediation exactly where it stopped — after a rate limit, a crash or a power cut. It is the single place that says what is done, what is half-done, and what to run next. **Update it after every step with `bash tools/sync_notes.sh "<status>"`** (it also mirrors this file and the progress log into the Obsidian vault on the bridge VM and pushes that repo).

## 0. Reading order for a cold start
1. `phd_experiments/CLAUDE.md` (project rules, owner decisions D-1…D-24; D-23/D-24 are from 26–27.10) and `phd_experiments/HANDOFF-experiments.md`.
2. This file.
3. `03_fix_plan.md` in this folder: §0 ground rules, §1 procedures (branch/deploy/verify/merge/rollback per repo), then the step you are on.
4. `04_progress_log.md`: one row per merged step.
5. Background only: `01_codex_review.md` (original review), `02_claude_corrected_review.md` (corrected, with N-001…N-014).

The owner's standing instruction (27.10.2026): implement the plan one step at a time **without asking**, safest method, every step revertable: **one branch per step** (`fix/<id>-<slug>`), merge `--no-ff` into `main` only when the step's test AND the full web-VM regression are green, tag `step-<id>-done`, push branch+merge+tag. Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Anything needing an owner ruling is NOT implemented (plan §6, O-1…O-8).

## 1. Where everything is
| What | Where |
|---|---|
| This PC (HP Desktop, `stefan-desktop`) | `C:\Users\stefan\Documents\aaPROJECTS_after_fable-dev\` — `PHD-FABLE_MAYA\` (not a git repo), `robco-control-center\` (W), `rb1-base-sim-noetic\` (S), `bridge_vm_ros1to2\` (B) |
| Web VM `webvm` 10.25.25.113 | `~/robco-control-center` (W; pulls only). Tests: `.venv/bin/pytest`, `./scripts/regression_suite.sh` |
| Bridge VM `bridge` 10.25.25.115 | `~/bridge-vm-config-repo` (B, pushes itself) and the live Obsidian vault `~/obsidian` |
| Sim VM `sim` 10.25.25.123 | `~/catkin_ws/src` (S; **no GitHub write** — push from this PC: `git fetch sim:catkin_ws/src main` then `git push origin FETCH_HEAD:refs/heads/main`) |
| Tags before the work | `pre-remediation-2026-10-27` in W, S and B; DB dump `~/backups/robco_pre-remediation_2026-10-27_0046.dump` on the web VM; unit-file and map backups in `~/backups/remediation-2026-10-27/` on sim and bridge |
| Helper scripts | `tools/wverify.sh <branch> <backend,nginx,gateway,none> [pytest files]` (deploys branch to the web VM, rebuilds, waits for `/api/health`, runs pytest + full suite); `tools/wmerge.sh <id> <branch> "<title>" <build-spec>` (merge --no-ff, tag, push, web VM back to `main`); `tools/capture_loop.sh N`, `tools/live13.sh` (live checks, run on the web VM with `ssh webvm 'bash -s' < script`); `tools/sync_notes.sh` |

## 2. State right now
(Keep this section current.)
- **Merged and tagged (W):** 1.1 estop transition, 1.2 estop state ordering, 1.3 estop survives restart, 1.4 teleop socket identity, 1.5 joystick release (blur/hidden/lost capture), 1.6 driver reservation by token, 1.7 idle teleop goes quiet, 1.8 teleop session re-check 2 s, 1.9 Argon2 off the loop, 1.10 mapping interlock. Suite 30/30, 209 pytest, ~97 Playwright. Baseline step 0 done.
- **Also merged:** 2.5a leaflet teardown (e277ab2) and 2.5 point capture needs a newer pose stamp (f014cc9). Suite 30/30, 215 pytest, 97 Playwright; 20/20 live captures. Web VM is back on `main`.
- **Open finding N-015:** forced no-motion updates from many captures collapse the AMCL particle cloud; recover with `bash tools/reseed_amcl.sh`; `tools/flake12.sh` runs serial flake checks with re-seed. Needs an owner ruling before capture behaviour changes (see progress log).
- **Also merged (S):** 2.6 keepalive replays only the live `/robot/amcl` (7f124fd, tag step-2.6-done); sim VM is on `main`, `amcl-pose-keepalive` active. Live checks script: `tools/live26.sh` (needs the catkin workspace sourced; do not use `rosnode info` right after `kill -9`, it hangs on the dead node).
- **Also merged (B):** 2.7 atomic map export + generation (654a2a0, tag step-2.7-done); exporter redeployed and running on the bridge.
- **Open finding N-016:** rosbridge restarts under test load make ~1 in 3 full-suite runs go red in capture specs (see progress log). A red suite in points/tasks/telemetry_panel: check `ssh bridge 'sudo journalctl -u rosbridge-health --since -15min | grep restarting'` first, then re-run once on a quiet system.
- **Next:** 2.1–2.4 and 2.8 (S, real mapping sessions — back up the map first, plan §1.3; 2.1 first), then 2.9–2.13, stage 3, stage 4. Order is binding where "Depends on" says so.

## 3. Pitfalls learned the hard way (do not repeat)
1. **Never run two Playwright/regression runs on the web VM at once.** They share users, `test-results/` and global setup/teardown; one run deletes the other's accounts and the other sees login failures. This produced several false reds on 27.10. Before starting a run: `ssh webvm 'pgrep -af playwright'` must be empty. Never use `&` for ssh test loops; use `run_in_background` and wait for the notification.
2. **Stale ROS 1 nodes make the bridge loop and the telemetry stall.** Leftover `rostopic`/`tf_echo` clients killed by `timeout` stay registered in the master; `ros1-dynamic-bridge` then logs "Failed to connect to 10.25.25.123:<port>" in a tight loop. Pre-flight before any live step: `ssh sim 'source /opt/ros/noetic/setup.bash; export ROS_MASTER_URI=http://10.25.25.123:11311; echo y | rosnode cleanup'` and `ssh bridge 'sudo journalctl -u ros1-dynamic-bridge --since -20sec | grep -c "Failed to connect"'` must be 0. Use `timeout -s INT` for ad-hoc ROS clients and do not leave any running.
3. **Addresses:** bridge 10.25.25.115, sim 10.25.25.123, web 10.25.25.113 (Omada reservations requested). 10.25.25.108 is an unrelated machine. Older docs say .107/.108/.115.
4. **The auto-mode classifier blocks** `systemctl enable`/new units, `ufw` changes, `StrictHostKeyChecking=no`; those need the owner's explicit OK in chat. Plan steps that install units or touch firewalls (4.3, 3.12 etc.) must ask first. Unit installs for the AMCL keepalive and firewall edits already done on 27.10 were approved by the owner.
5. **Shell quoting:** large multi-line Python via `python - <<'X'` in the Bash tool sometimes fails to parse; write the script to the scratchpad with the Write tool and run it. `python` on this PC is Windows-native: use `C:\...` paths inside Python, `/c/...` in bash.
6. The sim's `rostopic hz` on sim-time topics may print "no new messages" although data flows; verify with `echo -n1` or from the ROS 2 side (env: `env -i ... FASTRTPS_DEFAULT_PROFILES_FILE=/etc/robco/fastdds_udp_only.xml`, foxy sourced alone).
7. Dead-man/teleop Playwright specs and `points_ui` have been flaky for the causes in 1 and 2 above; a red full suite must be re-run once on a quiet system before being blamed on a change (baseline-before-blame, plan §0.3).
10. **Re-seed AMCL (`bash tools/reseed_amcl.sh`) before every full suite run** and after any mapping or kill test: a run forces ~100 no-motion updates and the particle cloud degrades. Even then ~1 in 3 runs can go red from rosbridge restarts (N-016); distinguish by the restart log, not by guessing.
9. **A wait loop that greps for its own command line never ends.** `while pgrep -f "playwright test"` inside `ssh ... 'bash -c ...'` matches itself, so the 27.10 flake check sat idle for hours without running a test. Never use `pgrep -f` on a string that appears in the command doing the waiting; give every wait a timeout; before reporting a background job as running, verify it (process list, load, fresh output).
8. Demo accounts `demo_admin|manager|technician|officer` exist on the web VM (temporary, password given to the owner in chat). Throwaway probe users use the prefix `fixprobe_` and are deleted in the same step.

## 4. Per-step routine (checklist)
1. `git checkout main && git pull` → new branch `fix/<id>-<slug>`; edit; commit; `git push -u origin <branch>`.
2. `bash tools/wverify.sh <branch> <build-spec> [pytest files]` → must end `REGRESSION SUITE GREEN` (re-run once if red, see pitfalls).
3. Live check if the step says so.
4. `bash tools/wmerge.sh <id> <branch> "<title>" <build-spec>`.
5. Append a row to `04_progress_log.md`; update §2 of this file; add the row to the Done log of `phd_experiments/HANDOFF-experiments.md` (batch per stage is acceptable but never skip) and new decisions to `phd_experiments/CLAUDE.md`.
6. `bash tools/sync_notes.sh "<status>"` (vault + bridge repo).
7. For S/B steps: also push from the correct machine (plan §1.3/§1.4) and tag.

## 5. If something is broken
- Roll a merged step back: `git revert -m 1 <merge sha>` in W (plan §1.2.7), push, redeploy, full suite; tag `step-<id>-reverted`.
- Web VM stuck on a branch: see §2. App unreachable: `ssh webvm 'cd ~/robco-control-center && docker compose ps'`.
- Sim not running: `ssh sim 'cd ~/catkin_ws/src && setsid nohup ./tools/run_neo_workshop.sh navigation > ~/nav.log 2>&1 < /dev/null &'` (starts the simulation; wait ~60–90 s; `gui:=false` is the default).
- Everything about the VMs and repos: Obsidian note `20-Infrastructure/Project Infrastructure 2026-10` in the vault.

---

# Remediation progress log (27.10.2026 →)

| Step | Finding ids | Repo | Merge SHA | Tag | Suite |
|---|---|---|---|---|---|
| 0 baseline | — | W,S,B | tags `pre-remediation-2026-10-27` | — | 30/30 (192 pytest, 94 PW) |
| 1.1 estop transition | F-003, F-016 | W | 73f4718 | step-1.1-done | 30/30 (192 pytest) — dead-man PW spec flaked once in a full run, green in isolation x2 and on rerun |
| 1.2 estop state order | F-003 | W | 33f2241 | step-1.2-done | 30/30 (192 pytest, vitest +6) |
| 1.3 estop restart | F-004, N-009 | W | ce10950 | step-1.3-done | 30/30 (197 pytest); live: engage->restart->restored->release verified |
| 1.4 teleop socket identity | N-001 | W | 6021dc0 | step-1.4-done | 30/30 |
| 1.5 joystick release | F-005, F-016 | W | 3094951 | step-1.5-done | 30/30, 96 PW |

**Operational finding (27.10, during 1.5):** two full-suite reds (telemetry_panel, teleop dead-man) were caused by a *stale ROS 1 node* left registered in the master by an earlier `rosrun tf tf_echo`/`rostopic` run killed by `timeout`. The bridge's dynamic_bridge then retried "Failed to connect to 10.25.25.123:<port>" in a tight loop and the telemetry stream stalled. Fix: `rosnode cleanup` on the sim. **Pre-flight for every live step: `ssh sim '... rosnode cleanup'` and check `journalctl -u ros1-dynamic-bridge --since -20sec | grep -c "Failed to connect"` is 0.** Never leave ad-hoc ROS clients running; use `timeout -s INT`.
| 1.6 driver reservation | F-002, N-005(d) | W | cecb391 | step-1.6-done | 30/30 (201 pytest, 97 PW) |
| 1.7 idle teleop quiet | N-002 | W | 7af3f20 | step-1.7-done | 30/30 (204 pytest); live rostopic check skipped, covered by unit + PW |
| 1.8 teleop recheck | N-014 | W | b4e7178 | step-1.8-done | 30/30 (205 pytest) |
| 1.9 argon2 off loop | F-007 | W | d34365a | step-1.9-done | 30/30 (206 pytest, 97 PW); one transient 6-test PW red right after the backend rebuild, green on rerun (suite now waits for /api/health) |
| 1.10 mapping interlock | F-009(1) | W | 6c7ad3a | step-1.10-done | 30/30 (209 pytest) |
| 2.5a leaflet teardown | (found in 2.5 verification) | W | e277ab2 | step-2.5a-done | 30/30 (209 pytest, 97 PW); points specs 12/12 clean serial runs (AMCL re-seeded each run) |
| 2.5 capture newer stamp | F-001 | W | f014cc9 | step-2.5-done | 30/30 (215 pytest, 97 PW); live: 20/20 captures OK |

**Finding N-015 (27.10, found while verifying 2.5):** every point capture forces a no-motion AMCL update; ~100+ of them (a long test loop) collapse the particle cloud (variance ~1e-13, can go negative), after which `stddev_xy` is null and the points specs fail. Recovery: `bash tools/reseed_amcl.sh` (initialpose in frame `robot_map` with covariance 0.25, then a forced update). Production risk: many captures in a row on the real robot. Not changed yet — needs an owner ruling (e.g. rate-limit forced updates or drop them when a fresh sample exists). Also: a flake-check wait loop that greps its own command line never ended and wasted hours; see handoff pitfall 9.
| 2.6 keepalive live AMCL | F-017 | S | 7f124fd (branch ede2dbb, 93d1ddb) | step-2.6-done | live (a)-(d) pass: silent <=2.5 s after rosnode kill and kill -9; relaunch publishes only the new run's pose (stamp 19 s old). Suite 30/30 (run 1 green, run 2 red in tasks/telemetry_panel specs that pass alone, retry green: 97 PW). Also: clean systemd stop (no traceback); stopped an orphaned second navigation launch (pid 18659 tree) on the sim |
| 2.7 atomic map export | F-012 (exporter) | B | 654a2a0 (branch 452d761) | step-2.7-done | refresh x2: same generation 74e40cd1c4da527c, new generated_at; 1000 reads during refreshes: 0 bad PNG (CRC-checked), 0 bad JSON; one refresh ~8 s (pre-existing cost). Suite 30/30 on the 4th attempt: earlier reds were capture specs hit by rosbridge restarts (N-016), not the exporter |

**Finding N-016 (29.10, found while verifying 2.7):** `rosbridge-health` restarts `rosbridge-websocket` after 3 consecutive probe-A timeouts (44 restarts in total; 3-4 per hour all day on 26.10; 5 between 10:02 and 10:28 UTC on 29.10, only while tests ran). A capture that lands in the ~5 s restart window gets a 409 ("no response from /robot/request_nomotion_update"), which since step 2.5 is refused instead of silently falling back to the last sample. Result: roughly one full-suite run in three goes red in capture-dependent specs (points, tasks, telemetry_panel) with no code fault; they pass alone and on re-run. The service itself answers in ~1.1 s (60/60 direct). Not changed. Options for the owner: (a) the backend retries the forced update once after a reconnect; (b) tests retry on 409; (c) find why rosbridge stalls under many clients (single-threaded python, probe timeout 5 s) and give it capacity or a longer probe timeout. Recommendation: (c) investigate, (a) as a cheap mitigation.
