# Open Questions

## AMCL Freshness

Question:
- Is `/robot/amcl_pose` actively publishing during normal sim operation?

Needed:
- Verify after ROS 1 master is restored and simulation is running.
- Check ROS 1, ROS 2, and websocket delivery.

## Frontend Pose Source

Question:
- Should the frontend temporarily use `/robot/robotnik_base_control/odom` if AMCL remains sparse?

Current preference:
- Keep `/robot/amcl_pose` as the preferred semantic pose topic.
- Use odom as fallback/diagnostic only unless product behavior requires otherwise.

## Production HTTP Serving

Question:
- Should Flask dev server be replaced with gunicorn or another WSGI server?

Current status:
- Werkzeug dev server is active and adequate for internal bridge usage so far.
- Logs warn it is not intended for production deployment.

## LXC Inventory

Question:
- Are there project LXCs outside this bridge VM that were not visible from local docs?

Current observed state:
- No LXC inventory was discovered locally.
- Known machines are `10.25.25.107`, `10.25.25.115`, and future web app VM `10.25.25.113`.
