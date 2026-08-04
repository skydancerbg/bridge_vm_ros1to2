#!/usr/bin/env bash
set -euo pipefail

export ROS_MASTER_URI=http://10.25.25.115:11311
export ROS_IP=10.25.25.108
export ROS_LOCALHOST_ONLY=0
# FastDDS shared memory is broken on this host (open_and_lock_file fails); UDP only.
export FASTRTPS_DEFAULT_PROFILES_FILE=/etc/robco/fastdds_udp_only.xml
unset ROS_HOSTNAME

set +u
source /opt/ros/noetic/setup.bash
source /opt/ros/foxy/setup.bash
set -u

# This script sources BOTH noetic and foxy, which breaks `rostopic`: the mixed PYTHONPATH makes
# it fail on import, so this check used to return failure unconditionally — the watchdog was
# half-blind and fell back to the ROS 2 check alone, restarting the bridge whenever that had a
# transient hiccup. Running rostopic in a subshell with the ROS 2 environment stripped fixes it.
# ROS_MASTER_URI and ROS_IP are deliberately left in place; only the distro paths are unset.
check_ros1_odom() {
  local info
  if ! info="$(timeout 8 env \
        -u PYTHONPATH -u CMAKE_PREFIX_PATH -u LD_LIBRARY_PATH -u AMENT_PREFIX_PATH \
        -u ROS_DISTRO -u ROS_VERSION -u ROS_PYTHON_VERSION -u ROS_ETC_DIR \
        -u ROS_PACKAGE_PATH -u ROS_ROOT -u ROSLISP_PACKAGE_DIRECTORIES \
        bash -c 'source /opt/ros/noetic/setup.bash >/dev/null 2>&1; \
                 rostopic info /robot/robotnik_base_control/odom' 2>/dev/null)"; then
    return 1
  fi
  sed -n '/^Publishers:/,/^Subscribers:/p' <<<"$info" | grep -q '^ \* '
}

# Run the ROS 2 probe under Foxy ALONE. This script sources noetic and foxy together, and in that
# mixed environment rclpy sees an empty graph -- measured: 0 messages and 0 publishers, against
# 1325 messages and 1 publisher for the same probe under Foxy alone. The check therefore used to
# fail unconditionally, so the watchdog restarted the bridge roughly once a minute, and every
# restart destroyed the ROS 2 publishers rosbridge had matched. That is what kept the browser
# read path dead. `env -i` is deliberate: inheriting anything from here reintroduces the fault.
check_ros2_odom() {
  env -i \
    HOME="${HOME:-/home/swu}" \
    PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    ROS_LOCALHOST_ONLY=0 \
    FASTRTPS_DEFAULT_PROFILES_FILE=/etc/robco/fastdds_udp_only.xml \
    timeout 45 bash -c '
      set +u
      source /opt/ros/foxy/setup.bash >/dev/null 2>&1
      set -u
      exec python3 /usr/local/bin/bridge_ros2_odom_probe.py
    ' >/dev/null 2>&1
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
    if (( ros2_failures >= 3 )); then
      echo "bridge watchdog: ROS 2 odom path unhealthy for an extended period, exiting for systemd restart" >&2
      kill "$bridge_pid" 2>/dev/null || true
      wait "$bridge_pid" || true
      exit 1
    fi
  fi

  sleep 10
done
