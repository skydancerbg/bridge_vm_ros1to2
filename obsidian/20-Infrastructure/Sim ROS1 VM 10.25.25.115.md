# Sim ROS1 VM 10.25.25.115

## Identity

Role:
- Upstream simulation and ROS 1 master VM.

Proxmox:
- Node/server: `aipve`
- VM ID: `12851`
- VM name: `u20-RB1sim-ros1and2-bridge-geminicli`

Primary endpoint:
- `http://10.25.25.115:11311`

Tailscale:
- `100.79.246.33`

Expected users:
- `swu`
- `root` if deeper sim-control access is needed.

## Responsibilities

Expected from project scripts and docs:
- Runs ROS 1 master.
- Runs simulation/navigation stack.
- Provides `/robot/static_map`.
- Publishes `/robot/amcl_pose`.
- Publishes `/robot/robotnik_base_control/odom`.
- Hosts restart script `/home/swu/restart_neo_workshop_navigation.sh`.
- Starts simulation/ROS master from `~/catkin_ws` with `roslaunch rb1_base_gazebo rb1_neo_workshop_navigation.launch`.

## Current Known State

Latest known state:
- On `2026-07-03`, ROS 1 master communication from `10.25.25.107` failed.
- On `2026-07-04`, the user started the simulation/ROS master and `/robot/static_map` was reachable from the bridge VM.
- Software inventory on this VM still needs direct inspection.

## Remote Helper Scripts

From bridge VM:

```bash
cd /home/swu/bridge-vm-config-repo
./scripts/remote_sim_status.sh
./scripts/remote_sim_restart.sh
```

## Simulation Start Command

Run on `10.25.25.115`:

```bash
cd ~/catkin_ws && source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch rb1_base_gazebo rb1_neo_workshop_navigation.launch
```

This starts the simulation and therefore starts ROS master for the bridge VM.

## Expected Restart Script

```bash
/home/swu/restart_neo_workshop_navigation.sh
```

Existing bridge repo scripts still point to `/home/swu/restart_neo_workshop_navigation.sh`.

## Related Notes

- [[40-Operations/Remote Sim Operations]]
- [[40-Operations/Recovery Playbooks]]
- [[90-Agent-Handoff/Open Questions]]
