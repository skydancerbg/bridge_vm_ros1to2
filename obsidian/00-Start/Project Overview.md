# Project Overview

## Goal

Keep the existing ROS 1 -> ROS 2 websocket bridge for live/light topics, and provide reliable HTTP delivery for large static map assets.

The frontend should use:
- `http://10.25.25.107:8081/map.png`
- `http://10.25.25.107:8081/map_meta.json`
- `ws://10.25.25.107:9090` for live topics such as `/robot/amcl_pose`

## Why This Exists

Large map delivery through rosbridge/browser was unreliable. The project therefore separates traffic by type:
- Static/heavy map data is exported once from ROS 1 and served by HTTP.
- Live/light robot topics stay on websocket through rosbridge.

## Current Runtime Shape

See [[10-Architecture/Runtime Architecture]] for details.

Current intended runtime:
- `ros1-dynamic-bridge.service`: ROS 1 -> ROS 2 dynamic bridge.
- `rosbridge-websocket.service`: ROS 2 websocket server on `9090`.
- `rosbridge-topic-advertiser.service`: topic type visibility helper for rosbridge.
- `ros-map-export.service`: HTTP map exporter on `8081`.

Legacy runtime:
- `ros-bridge.service` is masked and retired.

## Primary Documentation Sources

Live or staged docs:
- `/home/swu/bridge-docs`
- `/home/swu/bridge-vm-config-repo`
- `/home/swu/bridge-vm-config-repo/docs/Handoff_03-06-26_v1.md`

This vault summarizes those sources and the latest observed live system state.

## Related Notes

- [[00-Start/Current Status]]
- [[20-Infrastructure/Machines and Access]]
- [[30-Services/Service Inventory]]
- [[50-Development/What Was Developed]]
- [[60-Decisions/Decision Log]]

