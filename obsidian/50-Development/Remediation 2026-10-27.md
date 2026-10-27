# Remediation 2026-10-27 (mirror of phd_experiments/code_review_2026-10-27)

# HANDOFF — remediation of the 27.10.2026 code review (read this first in a new session)

**Last update:** 27.10.2026 21:29 — steps 1.1-1.10, 2.5a, 2.5 merged; next 2.6

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
- **Branch `fix/2.5-capture-newer-stamp` (W): pushed, NOT merged.** Point capture requires a newer pose stamp and a successful forced update (F-001). Verified: 215 pytest green; full suite flaked because of the unrelated issues below.
- **Branch `fix/2.5a-leaflet-teardown` (W): pushed, NOT merged.** (a) `map.stop()` before `map.remove()` and non-animated centring in `FacilityMap.jsx` — an uncaught Leaflet `_leaflet_pos` error appeared once the AMCL keepalive (D-24) made the first pose arrive at page load; (b) `points_ui.spec.js` compares the listed pose as a number (double-rounding bug in the test). A serial 12-run flake check of the points specs was running when this was written; merge 2.5a if it shows 0 failures, then `git merge main` into the 2.5 branch, re-verify, merge 2.5.
- **The web VM may still be checked out on a branch** (`fix/2.5a-leaflet-teardown`). Check with `ssh webvm 'git -C ~/robco-control-center branch --show-current'`; put it back on `main` (`git checkout main && git pull --ff-only`, rebuild what changed) before judging any result.
- **Next after 2.5/2.5a:** 2.6 (keepalive tied to the live `/robot/amcl`, S — fixes F-017, my own D-24 bug: after a SLAM session the keepalive replays the pre-session pose), then 2.7 (B), 2.1–2.4 and 2.8 (S, they run real mapping sessions — back up the map first, plan §1.3), 2.9–2.13, stage 3, stage 4. Order is binding where "Depends on" says so.

## 3. Pitfalls learned the hard way (do not repeat)
1. **Never run two Playwright/regression runs on the web VM at once.** They share users, `test-results/` and global setup/teardown; one run deletes the other's accounts and the other sees login failures. This produced several false reds on 27.10. Before starting a run: `ssh webvm 'pgrep -af playwright'` must be empty. Never use `&` for ssh test loops; use `run_in_background` and wait for the notification.
2. **Stale ROS 1 nodes make the bridge loop and the telemetry stall.** Leftover `rostopic`/`tf_echo` clients killed by `timeout` stay registered in the master; `ros1-dynamic-bridge` then logs "Failed to connect to 10.25.25.123:<port>" in a tight loop. Pre-flight before any live step: `ssh sim 'source /opt/ros/noetic/setup.bash; export ROS_MASTER_URI=http://10.25.25.123:11311; echo y | rosnode cleanup'` and `ssh bridge 'sudo journalctl -u ros1-dynamic-bridge --since -20sec | grep -c "Failed to connect"'` must be 0. Use `timeout -s INT` for ad-hoc ROS clients and do not leave any running.
3. **Addresses:** bridge 10.25.25.115, sim 10.25.25.123, web 10.25.25.113 (Omada reservations requested). 10.25.25.108 is an unrelated machine. Older docs say .107/.108/.115.
4. **The auto-mode classifier blocks** `systemctl enable`/new units, `ufw` changes, `StrictHostKeyChecking=no`; those need the owner's explicit OK in chat. Plan steps that install units or touch firewalls (4.3, 3.12 etc.) must ask first. Unit installs for the AMCL keepalive and firewall edits already done on 27.10 were approved by the owner.
5. **Shell quoting:** large multi-line Python via `python - <<'X'` in the Bash tool sometimes fails to parse; write the script to the scratchpad with the Write tool and run it. `python` on this PC is Windows-native: use `C:\...` paths inside Python, `/c/...` in bash.
6. The sim's `rostopic hz` on sim-time topics may print "no new messages" although data flows; verify with `echo -n1` or from the ROS 2 side (env: `env -i ... FASTRTPS_DEFAULT_PROFILES_FILE=/etc/robco/fastdds_udp_only.xml`, foxy sourced alone).
7. Dead-man/teleop Playwright specs and `points_ui` have been flaky for the causes in 1 and 2 above; a red full suite must be re-run once on a quiet system before being blamed on a change (baseline-before-blame, plan §0.3).
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
