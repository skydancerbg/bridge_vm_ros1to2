# set_GitHub_for_the_project

## Current Situation

The super repo is:

```bash
/home/swu/bridge-vm-config-repo
```

GitHub remote:

```text
https://github.com/skydancerbg/bridge_vm_ros1to2.git
```

The current non-interactive agent session cannot push over HTTPS because no GitHub credentials are available to it. SSH also fails unless this VM key is added to GitHub:

```text
git@github.com: Permission denied (publickey)
```

## Option 1: Use SSH Deploy/User Key

Add this public key to GitHub as a deploy key or user SSH key:

```bash
/home/swu/.ssh/id_rsa.pub
```

Repository:

```text
skydancerbg/bridge_vm_ros1to2
```

Then run:

```bash
cd /home/swu/bridge-vm-config-repo
git remote set-url origin git@github.com:skydancerbg/bridge_vm_ros1to2.git
git push origin main
```

## Option 2: Use HTTPS Credentials Or Token

Configure GitHub HTTPS credentials/token and run:

```bash
cd /home/swu/bridge-vm-config-repo
git push origin main
```

If Git prompts for credentials:
- Username: GitHub username.
- Password: GitHub personal access token, not account password.

## Check State

```bash
cd /home/swu/bridge-vm-config-repo
git status --short --branch
git remote -v
git log --oneline -5
```

Expected after successful push:

```text
## main...origin/main
```

No `ahead` marker should remain.

