#!/usr/bin/env bash
set -euo pipefail

SIM_HOST="${SIM_HOST:-10.25.25.123}"
SIM_USER="${SIM_USER:-swu}"
LOCAL_SSH_USER="${LOCAL_SSH_USER:-swu}"

echo "Restarting simulation on ${SIM_USER}@${SIM_HOST} via local user ${LOCAL_SSH_USER}"
echo "Note: if the previous sim launcher terminal is hung, clear it with Ctrl-C or close/kill that terminal on the sim VM."

exec sudo -u "${LOCAL_SSH_USER}" ssh -o BatchMode=yes "${SIM_USER}@${SIM_HOST}" '/home/swu/restart_neo_workshop_navigation.sh'
