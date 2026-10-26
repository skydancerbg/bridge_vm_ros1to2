# Address change 2026-10-26

DHCP drift moved the VMs; addresses were re-verified from Proxmox (node aipve) and are now reserved in Omada.
Older notes in this vault that mention .107 / .108 / .115 describe earlier states.

| VM | Proxmox ID | MAC | Address |
|---|---|---|---|
| Bridge (this VM, ros1ros2bridge) | 12800 | BC:24:11:6F:F9:51 | 10.25.25.115 |
| Web app (robotweb) | 12850 | BC:24:11:D4:ED:4C | 10.25.25.113 |
| Sim (rb1sim-phd) | 12851 | BC:24:11:2A:03:A3 | 10.25.25.123 |

10.25.25.108 is an unrelated machine (Uptime Kuma client). Do not allow it through any firewall.
