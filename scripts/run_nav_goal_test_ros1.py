#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time

import rospy
from actionlib_msgs.msg import GoalStatusArray
from geometry_msgs.msg import PoseStamped


GOALS = [
    {
        "x": -0.8399994969367981,
        "y": 0.040000155568122864,
        "z": 0.0,
        "qx": 0.0,
        "qy": 0.0,
        "qz": 0.850650975204773,
        "qw": 0.5257308421456446,
    },
    {
        "x": -2.1399996280670166,
        "y": 2.6600003242492676,
        "z": 0.0,
        "qx": 0.0,
        "qy": 0.0,
        "qz": 0.9998462378330013,
        "qw": 0.017535697624941393,
    },
    {
        "x": 3.379999876022339,
        "y": -0.139999657869339,
        "z": 0.0,
        "qx": 0.0,
        "qy": 0.0,
        "qz": 0.999263359277694,
        "qw": 0.03837627919767921,
    },
    {
        "x": -3.1399991512298584,
        "y": -6.680000305175781,
        "z": 0.0,
        "qx": 0.0,
        "qy": 0.0,
        "qz": 0.7000015201875764,
        "qw": 0.7141413527692414,
    },
]

TERMINAL = {
    2: "preempted",
    3: "reached",
    4: "aborted",
    5: "rejected",
    8: "recalled",
    9: "lost",
}
ACTIVE = {0: "pending", 1: "active", 6: "preempting", 7: "recalling"}


class StatusTracker:
    def __init__(self):
        self.by_id = {}
        self.last_msg_time = None
        rospy.Subscriber("/robot/move_base/status", GoalStatusArray, self._status_cb, queue_size=10)

    def _status_cb(self, msg):
        self.last_msg_time = time.monotonic()
        for entry in msg.status_list:
            self.by_id[entry.goal_id.id] = {
                "status": entry.status,
                "text": entry.text,
                "stamp_secs": entry.goal_id.stamp.secs,
                "stamp_nsecs": entry.goal_id.stamp.nsecs,
            }


def publish_goal(pub, frame_id, goal):
    msg = PoseStamped()
    msg.header.stamp = rospy.Time.now()
    msg.header.frame_id = frame_id
    msg.pose.position.x = goal["x"]
    msg.pose.position.y = goal["y"]
    msg.pose.position.z = goal["z"]
    msg.pose.orientation.x = goal["qx"]
    msg.pose.orientation.y = goal["qy"]
    msg.pose.orientation.z = goal["qz"]
    msg.pose.orientation.w = goal["qw"]
    pub.publish(msg)


def write_state(path, payload):
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="ascii") as handle:
        json.dump(payload, handle, sort_keys=True)
        handle.write("\n")
    os.replace(tmp_path, path)


def main():
    parser = argparse.ArgumentParser(description="Run captured nav goals through ROS 1 move_base.")
    parser.add_argument("--topic", default="/robot/move_base_simple/goal")
    parser.add_argument("--frame-id", default="robot_map")
    parser.add_argument("--goal-timeout-seconds", type=float, default=180.0)
    parser.add_argument("--accept-timeout-seconds", type=float, default=15.0)
    parser.add_argument("--state-file", default="/tmp/nav_goal_test/status.json")
    parser.add_argument("--stop-file", default="/tmp/nav_goal_test/stop.flag")
    args = parser.parse_args()

    rospy.init_node("run_nav_goal_test_ros1", anonymous=True)
    pub = rospy.Publisher(args.topic, PoseStamped, queue_size=10)
    tracker = StatusTracker()
    rate = rospy.Rate(10)
    os.makedirs(os.path.dirname(args.state_file), exist_ok=True)
    if os.path.exists(args.stop_file):
        os.remove(args.stop_file)
    write_state(
        args.state_file,
        {
            "pid": os.getpid(),
            "state": "starting",
            "current_goal_index": 0,
            "goal_id": None,
            "total_goals": len(GOALS),
        },
    )

    while pub.get_num_connections() == 0 and not rospy.is_shutdown():
        rate.sleep()

    for index, goal in enumerate(GOALS, start=1):
        known_ids = set(tracker.by_id.keys())
        print(f"sending goal {index}", flush=True)
        publish_goal(pub, args.frame_id, goal)
        start = time.monotonic()
        goal_id = None
        last_state = None
        write_state(
            args.state_file,
            {
                "pid": os.getpid(),
                "state": "goal_sent",
                "current_goal_index": index,
                "goal_id": None,
                "total_goals": len(GOALS),
            },
        )

        while not rospy.is_shutdown():
            now = time.monotonic()
            if os.path.exists(args.stop_file):
                print(f"goal {index} cancelled_by_operator", flush=True)
                write_state(
                    args.state_file,
                    {
                        "pid": os.getpid(),
                        "state": "cancelled",
                        "current_goal_index": index,
                        "goal_id": goal_id,
                        "total_goals": len(GOALS),
                    },
                )
                return 0
            if goal_id is None:
                new_ids = [gid for gid in tracker.by_id.keys() if gid not in known_ids]
                if new_ids:
                    goal_id = sorted(new_ids)[-1]
                    print(f"goal {index} accepted id={goal_id}", flush=True)
                    write_state(
                        args.state_file,
                        {
                            "pid": os.getpid(),
                            "state": "accepted",
                            "current_goal_index": index,
                            "goal_id": goal_id,
                            "total_goals": len(GOALS),
                        },
                    )
                elif now - start > args.accept_timeout_seconds:
                    print(f"goal {index} timeout no_status_id", flush=True)
                    write_state(
                        args.state_file,
                        {
                            "pid": os.getpid(),
                            "state": "accept_timeout",
                            "current_goal_index": index,
                            "goal_id": None,
                            "total_goals": len(GOALS),
                        },
                    )
                    break
            else:
                state = tracker.by_id.get(goal_id)
                if state is not None:
                    status = state["status"]
                    label = ACTIVE.get(status) or TERMINAL.get(status) or f"status_{status}"
                    if status != last_state and status in ACTIVE:
                        print(f"goal {index} {label}", flush=True)
                        write_state(
                            args.state_file,
                            {
                                "pid": os.getpid(),
                                "state": label,
                                "current_goal_index": index,
                                "goal_id": goal_id,
                                "total_goals": len(GOALS),
                            },
                        )
                        last_state = status
                    if status in TERMINAL:
                        text = state["text"] or TERMINAL[status]
                        print(f"goal {index} {TERMINAL[status]} text={text}", flush=True)
                        write_state(
                            args.state_file,
                            {
                                "pid": os.getpid(),
                                "state": TERMINAL[status],
                                "current_goal_index": index,
                                "goal_id": goal_id,
                                "status_text": text,
                                "total_goals": len(GOALS),
                            },
                        )
                        break
            if now - start > args.goal_timeout_seconds:
                print(f"goal {index} timeout exceeded {args.goal_timeout_seconds}s", flush=True)
                write_state(
                    args.state_file,
                    {
                        "pid": os.getpid(),
                        "state": "goal_timeout",
                        "current_goal_index": index,
                        "goal_id": goal_id,
                        "total_goals": len(GOALS),
                    },
                )
                break
            rate.sleep()

    write_state(
        args.state_file,
        {
            "pid": os.getpid(),
            "state": "completed",
            "current_goal_index": len(GOALS),
            "goal_id": None,
            "total_goals": len(GOALS),
        },
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
