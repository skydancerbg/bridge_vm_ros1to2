# Project Infrastructure (verified 2026-10-27)

Supersedes the address notes in older files of this vault (.107 / .108 / .115 were earlier states).

## Working directory (HP Desktop, hostname stefan-desktop, Windows 11)
- Dissertation + experiments: C:\Users\stefan\Documents\aaPROJECTS_after_fable-dev\PHD-FABLE_MAYA (entry: CLAUDE.md, phd_experiments\HANDOFF-experiments.md)
- Web app clone: C:\Users\stefan\Documents\aaPROJECTS_after_fable-dev\robco-control-center

## Virtual machines (Proxmox node aipve, Omada reservation by MAC)
| Role | Proxmox ID | Hostname | IP | MAC |
|---|---|---|---|---|
| Bridge (this VM) | 12800 | ros1ros2bridge | 10.25.25.115 | BC:24:11:6F:F9:51 |
| Web app | 12850 | robotweb | 10.25.25.113 | BC:24:11:D4:ED:4C |
| Sim | 12851 | rb1sim-phd | 10.25.25.123 | BC:24:11:2A:03:A3 |

10.25.25.108 is an unrelated machine; never allow it through a firewall.

## Repositories (GitHub account skydancerbg)
- robco-control-center (private): web app; clone on web VM ~/robco-control-center
- bridge_vm_ros1to2: this VM, ~/bridge-vm-config-repo (contains this vault under obsidian/)
- rb1-base-sim-noetic: sim VM ~/catkin_ws/src (no GitHub write from the VM: fetch to the HP Desktop and push there)

## Ports
web 80; bridge 9090 rosbridge, 8081 map; sim 11311 ROS master, 8080 video, 8090 map manager.

## Sim VM units
xvfb, web-video-server, robco-map-manager, amcl-pose-keepalive (re-sends the last AMCL pose each second so a console opened later shows the marker).

## Where to continue
See [[Current Status]] and the HANDOFF files in the dissertation project folder.
