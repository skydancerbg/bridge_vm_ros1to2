# CURRENT STAGE

## Current Stage
- Bridge VM is in post-fix stabilization stage with working split bridge services and recovered UI robot motion.

## Goal Of This Stage
- Keep the current working bridge state documented, reproducible, and protected against recurrence of rogue runtime ownership.

## Done In Previous Stages
- Implemented and verified `ros-map-export.service`.
- Exposed static map artifacts on HTTP port `8081`.
- Completed bridge-side map cropping against the real ROS occupancy grid, then rolled that change back to restore full-map export behavior.
- Retired the old combined `ros-bridge.service` runtime approach.
- Split the bridge into `ros1-dynamic-bridge.service` and `rosbridge-websocket.service`.
- Removed rogue unmanaged bridge runtime ownership, restarted the managed bridge services, and verified live ROS 2 and websocket delivery for `/robot/robotnik_base_control/odom`.

## In Scope Now
- Documentation and sync hygiene for the now-working post-fix bridge state.
- Commit preparation and mirrored-file consistency.
- Light operational guardrails that keep the legacy combined bridge path non-authoritative.

## Out Of Scope Now
- Redesigning the bridge architecture.
- Changing map export service behavior without a concrete map-export issue.
- Frontend redesign or unrelated application changes.

## Next Stages
- Re-check live `/robot/amcl_pose` behavior only if frontend requirements change.
- Keep using `/robot/robotnik_base_control/odom` as the primary bridge-health topic.
- Preserve the first-response troubleshooting rule before editing service files.
- Commit and preserve the current working mirror state.

## Risks / Watchouts
- Reverting the ROS 2-only rosbridge subprocess isolation can break DDS discovery again.
- Allowing a legacy or unmanaged bridge process to reclaim port `9090` can recreate the previous failure mode.
- Upstream ROS 1 publish behavior can still make AMCL appear stale even when odom is healthy.
