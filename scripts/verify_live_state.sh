#!/usr/bin/env bash
set -euo pipefail

systemctl status ros1-dynamic-bridge.service --no-pager -l | sed -n '1,20p'
printf '\n---\n'
systemctl status rosbridge-websocket.service --no-pager -l | sed -n '1,20p'
printf '\n---\n'
systemctl status rosbridge-topic-advertiser.service --no-pager -l | sed -n '1,20p'
printf '\n---\n'
systemctl status ros-map-export.service --no-pager -l | sed -n '1,20p'
printf '\n---\n'
curl -sS http://127.0.0.1:8081/map_meta.json
printf '\n---\n'
ss -ltnp | grep 9090
