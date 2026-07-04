# Recovery Playbooks

## Upstream ROS 1 Master Down

Symptoms:
- `rosservice info /robot/static_map` fails.
- Dynamic bridge logs show XML-RPC connection refused.
- `/refresh` on map exporter returns busy or times out.

Actions:
1. Check access to `10.25.25.115`.
2. Run remote sim status if SSH works.
3. Restart the sim/navigation stack on `10.25.25.115` if appropriate.
4. Re-run ROS 1 master checks from the bridge VM.
5. Re-run `curl http://127.0.0.1:8081/refresh`.

Commands:

```bash
cd /home/swu/bridge-vm-config-repo
./scripts/remote_sim_status.sh
./scripts/remote_sim_restart.sh
```

## Map HTTP Down

Symptoms:
- `curl http://127.0.0.1:8081/` fails.
- `ss` does not show `:8081`.

Actions:

```bash
systemctl status ros-map-export.service --no-pager -l
journalctl -u ros-map-export.service -n 80 --no-pager -l
sudo systemctl restart ros-map-export.service
```

Check:

```bash
curl -sS http://127.0.0.1:8081/map_meta.json
```

## Websocket Down

Symptoms:
- Frontend cannot connect to `ws://10.25.25.107:9090`.
- `ss` does not show `:9090`.

Actions:

```bash
systemctl status rosbridge-websocket.service --no-pager -l
ss -ltnp | grep 9090
journalctl -u rosbridge-websocket.service -n 80 --no-pager -l
sudo systemctl restart rosbridge-websocket.service
```

If a rogue process owns `9090`, stop it before restarting the managed service.

## ROS 2 Topic Types Missing

Symptoms:
- Rosbridge subscription complains about unknown topic type.
- Browser cannot subscribe to `/robot/amcl_pose` or odom despite websocket being up.

Actions:

```bash
systemctl status rosbridge-topic-advertiser.service --no-pager -l
sudo systemctl restart rosbridge-topic-advertiser.service
sudo systemctl restart rosbridge-websocket.service
```

## Dynamic Bridge Unhealthy

Symptoms:
- ROS 1 master is reachable, but topics do not appear in ROS 2.
- `dynamic_bridge` is missing or repeatedly restarting.

Actions:

```bash
systemctl status ros1-dynamic-bridge.service --no-pager -l
journalctl -u ros1-dynamic-bridge.service -n 100 --no-pager -l
sudo systemctl restart ros1-dynamic-bridge.service
```

## Do Not Use Legacy Combined Service

Do not unmask or restart `ros-bridge.service` unless intentionally rolling back from the split architecture.

Use:
- `ros1-dynamic-bridge.service`
- `rosbridge-websocket.service`
- `rosbridge-topic-advertiser.service`
- `ros-map-export.service`

