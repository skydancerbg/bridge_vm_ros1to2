# Machines and Access

## Known Machines

| Role | IP | User Access | Notes |
| --- | --- | --- | --- |
| Proxmox server/node | `aipve` | Proxmox admin access needed | Hosts the known project VMs. |
| Bridge VM | `10.25.25.107` | `swu`, sudo needed | VM ID `12800`, name `u20-ROS1ROS2-bridge`; hostname observed as `ros1ros2bridge`; runs bridge and map services. |
| Bridge VM Tailscale | `100.102.124.43` | Tailscale-dependent | Tailscale address on bridge VM. |
| Upstream sim / ROS 1 master | `10.25.25.115` | `swu`, `root` if needed | VM ID `12851`, name `u20-RB1sim-ros1and2-bridge-geminicli`; provides ROS 1 master at `http://10.25.25.115:11311`. |
| Upstream sim Tailscale | `100.79.246.33` | Tailscale-dependent | Tailscale address supplied on `2026-07-04`. |
| Future Robot Control Center web app | `10.10.25.113` | `swu`, sudo needed | VM ID `12850`, name `u24ai-RobcoGADGET-web`; future web app development target. |
| Future web app Tailscale | `100.121.18.83` | Tailscale-dependent | Tailscale address supplied on `2026-07-04`. |
| Gateway | `10.25.25.1` | N/A | Default route for bridge VM LAN. |

## LXC Status

No project LXC containers were discovered from the available local documentation or current bridge VM inspection. The known project machines are VMs/hosts listed above.

If another environment uses LXCs, add them here with:
- LXC host IP.
- Container name.
- Container IP.
- Required users.
- Purpose in the ROS/frontend chain.

## Bridge VM Network

Observed bridge VM interfaces:
- `enp6s18`: `10.25.25.107/24`
- `tailscale0`: `100.102.124.43/32`
- `lo`: `127.0.0.1/8`

Observed routes:
- Default via `10.25.25.1`
- LAN route `10.25.25.0/24` via `enp6s18`

## Passwordless Access Required For New Development VM

Required:
- `swu@10.25.25.107`
- Passwordless or otherwise non-interactive sudo on `10.25.25.107`
- `swu@10.25.25.115`
- `swu@10.10.25.113`
- Passwordless or otherwise non-interactive sudo on `10.10.25.113`

Needed for deeper sim control if required:
- `root@10.25.25.115`

Optional but useful:
- `root@10.25.25.107`, if root-level service edits should be direct instead of sudo through `swu`.

## SSH Setup From Windows 11

See [[40-Operations/Windows SSH Access Setup]].

## Related Notes

- [[20-Infrastructure/Bridge VM 10.25.25.107]]
- [[20-Infrastructure/Sim ROS1 VM 10.25.25.115]]
- [[20-Infrastructure/Web App VM 10.10.25.113]]
- [[40-Operations/Remote Sim Operations]]
- [[90-Agent-Handoff/Agent Quickstart]]
