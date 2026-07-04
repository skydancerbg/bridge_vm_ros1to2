# Web App VM 10.25.25.113

## Identity

Role:
- Future Robot Control Center / RobcoGADGET web app development VM.

Proxmox:
- Node/server: `aipve`
- VM ID: `12850`
- VM name: `u24ai-RobcoGADGET-web`

Network:
- LAN IP: `10.25.25.113`
- Tailscale IP: `100.121.18.83`

Expected access:
- `user@10.25.25.113`
- Sudo-capable access for runtime/deployment work.

## Expected Integration With Bridge VM

The web app should consume bridge VM endpoints:
- Map PNG: `http://10.25.25.107:8081/map.png`
- Map metadata: `http://10.25.25.107:8081/map_meta.json`
- Live websocket: `ws://10.25.25.107:9090`

It should not directly depend on ROS 1 master, ROS 1 service types, or sim VM internals.

## Related Notes

- [[10-Architecture/Runtime Architecture]]
- [[70-References/Topics and Data Contracts]]
- [[50-Development/Model Routing Guide]]
