# CURRENT STAGE

## Current Stage
- Bridge VM is in stabilization stage for full-map export and split bridge services.

## Goal Of This Stage
- Keep the bridge services stable, documented, and resumable while confirming reliable frontend-consumable pose delivery.

## Done In Previous Stages
- Implemented and verified `ros-map-export.service`.
- Exposed static map artifacts on HTTP port `8081`.
- Completed bridge-side map cropping against the real ROS occupancy grid, then rolled that change back to restore full-map export behavior.
- Retired the old combined `ros-bridge.service` runtime approach.
- Split the bridge into `ros1-dynamic-bridge.service` and `rosbridge-websocket.service`.
- Verified live ROS 2 and websocket delivery for `/robot/robotnik_base_control/odom`.

## In Scope Now
- Bridge-side verification of frontend-consumed pose topics under the split service architecture.
- Documentation and sync hygiene for clean resume.
- Ensuring frontend consumers use the current full-map metadata from the exporter.
- Careful service-level checks using `systemctl`, socket inspection, ROS topic inspection, and websocket subscription tests.

## Out Of Scope Now
- Redesigning the bridge architecture.
- Changing map export service behavior without a concrete map-export issue.
- Frontend redesign or unrelated application changes.

## Next Stages
- Re-check live `/robot/amcl_pose` behavior when upstream AMCL is actively updating.
- Decide whether frontend should temporarily prefer `/robot/robotnik_base_control/odom` if AMCL remains sparse.
- Keep frontend map consumption aligned with current exported metadata rather than cached cropped-map assumptions.
- Continue bridge-side verification only as needed to support frontend data flow.

## Risks / Watchouts
- Reverting the ROS 2-only rosbridge subprocess isolation can break DDS discovery again.
- Mixed ROS environment handling in `/usr/local/bin/bridge_startup.sh` is sensitive.
- Upstream ROS 1 publish behavior can make a bridge look unhealthy even when service wiring is correct.
