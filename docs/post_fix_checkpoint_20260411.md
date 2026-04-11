# Post-Fix Checkpoint 2026-04-11

- Root cause: an extra unmanaged `dynamic_bridge` process was running outside `ros1-dynamic-bridge.service`, which left the managed bridge/runtime state inconsistent and prevented stable rosbridge publish delivery.
- Runtime actions: killed the rogue root-owned bridge process, restarted `ros1-dynamic-bridge.service`, restarted `rosbridge-websocket.service`, and confirmed local rosbridge odom publish delivery.
- Hardening: masked the legacy `ros-bridge.service` name and moved its old unit file aside to prevent accidental reuse of the combined bridge path.
- Current validation: `9090` is owned by the managed rosbridge service, ROS 2 odom is live, local websocket subscriptions receive odom publish frames, and the UI is showing the robot moving again.
