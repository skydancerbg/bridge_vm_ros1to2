# CURRENT STAGE

## Current Stage
- Bridge VM is in stabilization stage for full-map export, split bridge services, and repeatable navigation testing.

## Goal Of This Stage
- Keep the bridge services stable, documented, and resumable while supporting repeatable bridge-side nav testing and preserving the post-fix transport behavior.

## Done In Previous Stages
- Implemented and verified `ros-map-export.service`.
- Exposed static map artifacts on HTTP port `8081`.
- Completed bridge-side map cropping against the real ROS occupancy grid, then rolled that change back to restore full-map export behavior.
- Retired the old combined `ros-bridge.service` runtime approach.
- Split the bridge into `ros1-dynamic-bridge.service` and `rosbridge-websocket.service`.
- Verified live ROS 2 and websocket delivery for `/robot/robotnik_base_control/odom`.
- Hardened `ros1_dynamic_bridge_watchdog.sh` so ROS 1 publisher absence alone no longer forces restarts; restart now requires ROS 1 publisher missing and unhealthy ROS 2 bridged odom for 3 consecutive checks.
- Captured 4 RViz 2D Nav Goals and added repeatable nav-goal test helpers on the bridge side.
- Documented the bridge-to-sim SSH workflow and remote sim restart entrypoint.

## In Scope Now
- Bridge-side verification of frontend-consumed pose topics under the split service architecture.
- Documentation and sync hygiene for clean resume.
- Ensuring frontend consumers use the current full-map metadata from the exporter.
- Careful service-level checks using `systemctl`, socket inspection, ROS topic inspection, and websocket subscription tests.
- Supporting repeatable status-driven nav-goal runs and remote sim-control/testing from the bridge repo.

## Out Of Scope Now
- Redesigning the bridge architecture.
- Changing map export service behavior without a concrete map-export issue.
- Frontend redesign or unrelated application changes.

## Next Stages
- Re-check live `/robot/amcl_pose` behavior when upstream AMCL is actively updating.
- Decide whether frontend should temporarily prefer `/robot/robotnik_base_control/odom` if AMCL remains sparse.
- Keep frontend map consumption aligned with current exported metadata rather than cached cropped-map assumptions.
- Continue bridge-side verification only as needed to support frontend data flow.
- Focus remaining investigation on visual smoothing and jumpiness rather than major transport collapse.

## Risks / Watchouts
- Reverting the ROS 2-only rosbridge subprocess isolation can break DDS discovery again.
- Mixed ROS environment handling in `/usr/local/bin/bridge_startup.sh` is sensitive.
- Upstream ROS 1 publish behavior can make a bridge look unhealthy even when service wiring is correct.
- Restore operations must include `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh` or the current `ros1-dynamic-bridge.service` unit will be incomplete.
- A sim restart can leave the prior remote launcher terminal hung; clear it before assuming the bridge recovery path is still bad.
