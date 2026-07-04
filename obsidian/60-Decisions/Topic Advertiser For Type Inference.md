# Topic Advertiser For Type Inference

## Decision

Run a small ROS 2 helper that advertises important topic names and types for rosbridge.

## Reason

Browser websocket subscriptions may not always provide enough type information. Keeping these types visible in ROS 2 helps rosbridge resolve subscriptions.

## Implementation

Service:
- `rosbridge-topic-advertiser.service`

Script:
- `/home/swu/bridge_support/ros2_topic_advertiser.py`

Advertised topics:
- `/robot/robotnik_base_control/odom`
- `/robot/amcl_pose`

## Guardrail

This helper is for type visibility, not data publication.

