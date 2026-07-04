# Windows SSH Access Setup

These commands are for Windows 11 PowerShell on the new development VM or Windows workstation.

## Generate Key

```powershell
$KeyName = "bridge_project_ed25519"
$Key = "$env:USERPROFILE\.ssh\$KeyName"
ssh-keygen -t ed25519 -a 100 -f $Key -C "bridge-project-new-vm" -N ""
```

## Install Key For Normal Access

```powershell
Get-Content "$Key.pub" | ssh swu@10.25.25.107 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
Get-Content "$Key.pub" | ssh swu@10.25.25.115 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
Get-Content "$Key.pub" | ssh swu@10.10.25.113 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

## Install Key For Root Access Where Needed

```powershell
Get-Content "$Key.pub" | ssh root@10.25.25.115 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

## Enable Passwordless Sudo For `swu` On Bridge VM

```powershell
ssh swu@10.25.25.107 "echo 'swu ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/90-swu-nopasswd && sudo chmod 440 /etc/sudoers.d/90-swu-nopasswd && sudo visudo -cf /etc/sudoers.d/90-swu-nopasswd"
```

## Enable Passwordless Root SSH On Bridge VM

```powershell
Get-Content "$Key.pub" | ssh swu@10.25.25.107 "sudo mkdir -p /root/.ssh && sudo chmod 700 /root/.ssh && sudo tee -a /root/.ssh/authorized_keys >/dev/null && sudo chmod 600 /root/.ssh/authorized_keys"
```

## Test Access

```powershell
ssh -i $Key swu@10.25.25.107 "hostname && sudo -n true && echo sudo-ok"
ssh -i $Key swu@10.25.25.115 "hostname"
ssh -i $Key swu@10.10.25.113 "hostname && sudo -n true && echo sudo-ok"
ssh -i $Key root@10.25.25.115 "hostname"
ssh -i $Key root@10.25.25.107 "hostname"
```

## Optional SSH Config

```powershell
@"
Host bridge-vm
  HostName 10.25.25.107
  User swu
  IdentityFile $Key

Host bridge-vm-root
  HostName 10.25.25.107
  User root
  IdentityFile $Key

Host sim-vm
  HostName 10.25.25.115
  User swu
  IdentityFile $Key

Host sim-vm-root
  HostName 10.25.25.115
  User root
  IdentityFile $Key

Host robcogadget-web
  HostName 10.10.25.113
  User swu
  IdentityFile $Key
"@ | Add-Content "$env:USERPROFILE\.ssh\config"
```
