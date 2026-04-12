#!/usr/bin/env bash
set -euo pipefail

export ROS_MASTER_URI=http://10.25.25.115:11311
export ROS_IP=10.25.25.107
export ROS_LOCALHOST_ONLY=0
unset ROS_HOSTNAME

set +u
source /opt/ros/noetic/setup.bash
source /opt/ros/foxy/setup.bash
set -u

check_ros1_odom() {
  local info
  if ! info="$(timeout 5 rostopic info /robot/robotnik_base_control/odom 2>/dev/null)"; then
    return 1
  fi
  sed -n '/^Publishers:/,/^Subscribers:/p' <<<"$info" | grep -q '^ \* '
}

check_ros2_odom() {
  timeout 6 python3 - <<'PY'
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

class Probe(Node):
    def __init__(self):
        super().__init__('bridge_odom_watchdog')
        self.count = 0
        self.create_subscription(Odometry, '/robot/robotnik_base_control/odom', self.cb, 10)

    def cb(self, _msg):
        self.count += 1

rclpy.init()
node = Probe()
for _ in range(6):
    rclpy.spin_once(node, timeout_sec=0.5)
    if node.count > 0:
        break
node.destroy_node()
rclpy.shutdown()
raise SystemExit(0 if node.count > 0 else 1)
PY
}

cleanup() {
  if [[ -n "${bridge_pid:-}" ]] && kill -0 "$bridge_pid" 2>/dev/null; then
    kill "$bridge_pid" 2>/dev/null || true
    wait "$bridge_pid" || true
  fi
}

trap cleanup EXIT INT TERM

ros2 run ros1_bridge dynamic_bridge --bridge-all-topics &
bridge_pid=$!

# Allow the bridge to build its initial graph before starting health checks.
sleep 12

combined_failures=0
ros2_failures=0
while true; do
  if ! kill -0 "$bridge_pid" 2>/dev/null; then
    wait "$bridge_pid"
    exit $?
  fi

  if ! check_ros1_odom; then
    if check_ros2_odom; then
      combined_failures=0
      ros2_failures=0
    else
      combined_failures=$((combined_failures + 1))
      ros2_failures=0
    fi

    if (( combined_failures >= 3 )); then
      echo "bridge watchdog: ROS 1 odom publisher missing and ROS 2 odom path unhealthy, exiting for systemd restart" >&2
      kill "$bridge_pid" 2>/dev/null || true
      wait "$bridge_pid" || true
      exit 1
    fi
  else
    combined_failures=0
    if check_ros2_odom; then
      ros2_failures=0
    else
      ros2_failures=$((ros2_failures + 1))
    fi

    # Require a longer sustained ROS 2-side failure before restarting the bridge.
    # This avoids bouncing the bridge on short navigation-time hiccups while
    # still recovering from a wedged ROS 1 -> ROS 2 odom path.
    if (( ros2_failures >= 6 )); then
      echo "bridge watchdog: ROS 2 odom path unhealthy for an extended period, exiting for systemd restart" >&2
      kill "$bridge_pid" 2>/dev/null || true
      wait "$bridge_pid" || true
      exit 1
    fi
  fi

  sleep 10
done
