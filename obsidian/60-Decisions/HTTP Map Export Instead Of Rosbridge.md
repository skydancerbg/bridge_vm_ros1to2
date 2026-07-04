# HTTP Map Export Instead Of Rosbridge

## Decision

Serve static map assets over HTTP on port `8081` instead of sending large map data through rosbridge/browser.

## Reason

Large map delivery through rosbridge/browser was unreliable. HTTP file serving is simpler, easier to cache, and decouples the frontend from ROS 1 service details.

## Implementation

Service:
- `ros-map-export.service`

Files:
- `/home/swu/map_exporter/app.py`
- `/home/swu/map_exporter/run.sh`

Endpoints:
- `/map.png`
- `/map_meta.json`
- `/refresh`

## Consequences

Positive:
- Frontend map loading is reliable and simple.
- Static map no longer stresses websocket transport.
- ROS 1 specifics stay behind the bridge VM.

Tradeoff:
- Map may be stale if ROS 1 master is unavailable and `/refresh` cannot complete.

