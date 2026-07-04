# Split Bridge Services

## Decision

Retire the combined bridge service and use separate systemd units for bridge, websocket, type advertising, and map export.

## Reason

Separate services isolate failure modes and make recovery clearer:
- Dynamic bridge can restart independently.
- Rosbridge can stay in a ROS 2-only environment.
- Map exporter can serve cached files even when ROS 1 is down.
- Type advertiser can be restarted without disturbing other pieces.

## Current Services

- `ros1-dynamic-bridge.service`
- `rosbridge-websocket.service`
- `rosbridge-topic-advertiser.service`
- `ros-map-export.service`

## Retired

- `ros-bridge.service`

## Guardrail

Do not unmask or restart `ros-bridge.service` during normal development.

