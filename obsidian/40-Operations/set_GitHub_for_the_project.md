# set_GitHub_for_the_project

## Current Working Setup

The super repo is:

```bash
/home/swu/bridge-vm-config-repo
```

GitHub repository:

```text
skydancerbg/bridge_vm_ros1to2
```

The deploy key is now installed and SSH authentication works from this bridge VM.

Verified command:

```bash
ssh -o BatchMode=yes -T git@github.com
```

Expected successful output:

```text
Hi skydancerbg/bridge_vm_ros1to2! You've successfully authenticated, but GitHub does not provide shell access.
```

Current Git remote is SSH:

```text
origin git@github.com:skydancerbg/bridge_vm_ros1to2.git
```

## Push Command

Use:

```bash
cd /home/swu/bridge-vm-config-repo
git push origin main
```

Successful no-op output when already current:

```text
Everything up-to-date
```

## If Remote Is Accidentally Reset To HTTPS

Restore SSH remote:

```bash
cd /home/swu/bridge-vm-config-repo
git remote set-url origin git@github.com:skydancerbg/bridge_vm_ros1to2.git
git push origin main
```

## Original Fallback: HTTPS Token

If SSH stops working, configure GitHub HTTPS credentials/token and run:

```bash
cd /home/swu/bridge-vm-config-repo
git remote set-url origin https://github.com/skydancerbg/bridge_vm_ros1to2.git
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

Expected when clean and pushed:

```text
## main...origin/main
origin  git@github.com:skydancerbg/bridge_vm_ros1to2.git (fetch)
origin  git@github.com:skydancerbg/bridge_vm_ros1to2.git (push)
```

No `ahead` marker should remain.

