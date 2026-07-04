# Remote Sim Operations

## Target

Upstream sim / ROS 1 master VM:
- `10.25.25.115`

Expected users:
- `swu`
- `root` when deeper control is needed

## Helper Scripts

Run from bridge VM:

```bash
cd /home/swu/bridge-vm-config-repo
./scripts/remote_sim_status.sh
./scripts/remote_sim_restart.sh
```

Defaults:
- `SIM_HOST=10.25.25.115`
- `SIM_USER=swu`
- `LOCAL_SSH_USER=swu`

Override example:

```bash
SIM_USER=root ./scripts/remote_sim_status.sh
```

## Expected Remote Restart Script

On `10.25.25.115`:

```bash
/home/swu/restart_neo_workshop_navigation.sh
```

## Manual Simulation Start Command

Run on `10.25.25.115`:

```bash
cd ~/catkin_ws && source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash && roslaunch rb1_base_gazebo rb1_neo_workshop_navigation.launch
```

This starts the simulation and therefore starts ROS master.

## Known Caution

A previous sim launcher terminal can remain hung after restart attempts. Clear it with `Ctrl-C` or close/kill that terminal on the sim VM before assuming bridge recovery is bad.

## Process Names To Inspect

Look for:
- `rb1_neo_workshop_navigation`
- `roslaunch`
- `gzserver`
- `gzclient`
- `gazebo`

## Related Notes

- [[20-Infrastructure/Machines and Access]]
- [[40-Operations/Recovery Playbooks]]
