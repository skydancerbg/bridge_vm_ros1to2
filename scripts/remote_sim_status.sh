#!/usr/bin/env bash
set -euo pipefail

SIM_HOST="${SIM_HOST:-10.25.25.123}"
SIM_USER="${SIM_USER:-swu}"
LOCAL_SSH_USER="${LOCAL_SSH_USER:-swu}"

sudo -u "${LOCAL_SSH_USER}" ssh -o BatchMode=yes "${SIM_USER}@${SIM_HOST}" '
echo "HOST $(hostname)"
echo "TIME $(date -Is)"
echo "RESTART_SCRIPT $(test -x /home/swu/restart_neo_workshop_navigation.sh && echo present || echo missing)"
echo "PROCESS_CHECK"
ps -ef | egrep "rb1_neo_workshop_navigation|roslaunch|gzserver|gzclient|gazebo" | grep -v grep || true
'
