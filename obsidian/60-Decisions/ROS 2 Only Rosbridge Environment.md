# ROS 2 Only Rosbridge Environment

## Decision

Run `rosbridge-websocket.service` in a ROS 2-only environment.

## Reason

Mixing ROS 1 and ROS 2 environment variables inside rosbridge can cause discovery and type-resolution problems. Rosbridge should see the ROS 2 graph produced by the dynamic bridge.

## Implementation

The unit unsets ROS 1 variables before sourcing Foxy:
- `ROS_MASTER_URI`
- `ROS_ETC_DIR`
- `ROS_PACKAGE_PATH`
- `ROS_ROOT`
- `ROSLISP_PACKAGE_DIRECTORIES`
- `ROS_VERSION`
- `ROS_DISTRO`
- `ROS_HOSTNAME`

Then it sources:
- `/opt/ros/foxy/setup.bash`

## Guardrail

Do not source `/opt/ros/noetic/setup.bash` inside `rosbridge-websocket.service`.

