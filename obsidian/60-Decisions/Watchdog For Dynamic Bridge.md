# Watchdog For Dynamic Bridge

## Decision

Run the dynamic bridge through `/usr/local/bin/ros1_dynamic_bridge_watchdog.sh`.

## Reason

The bridge can look unhealthy when upstream ROS 1 publishers temporarily disappear. Immediate restarts caused avoidable instability.

The watchdog requires sustained evidence before exiting and letting systemd restart the service.

## Behavior

The watchdog checks:
- ROS 1 odom publisher presence.
- ROS 2 bridged odom message flow.

It restarts after:
- ROS 1 odom publisher missing and ROS 2 odom unhealthy for repeated checks.
- ROS 2 odom path unhealthy for an extended period even when ROS 1 publisher exists.

## Guardrail

Do not simplify this back to a naive restart-on-first-failure check.

