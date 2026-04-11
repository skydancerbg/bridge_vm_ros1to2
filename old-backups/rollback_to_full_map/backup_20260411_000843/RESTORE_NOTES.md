# Restore Notes

Restore files to their original absolute paths.

- /usr/local/bin/bridge_startup.sh: legacy bridge startup helper.
- /etc/systemd/system/ros1-dynamic-bridge.service: managed ROS 1 to ROS 2 bridge service.
- /etc/systemd/system/rosbridge-websocket.service: managed websocket bridge service.
- /etc/systemd/system/ros-map-export.service: map exporter systemd unit.
- /home/swu/map_exporter/app.py: map exporter application logic.
- /home/swu/map_exporter/run.sh: map exporter launcher.
- /home/swu/bridge-docs/AGENTS.md: bridge VM responsibility notes.
- /home/swu/bridge-docs/PROJECT_STATUS.md: current bridge status.
- /home/swu/bridge-docs/CURRENT_STAGE.md: current bridge stage.

After restore:
- run: systemctl daemon-reload
- restart as needed: systemctl restart ros-map-export.service
- verify split bridge services: systemctl status ros1-dynamic-bridge.service rosbridge-websocket.service
