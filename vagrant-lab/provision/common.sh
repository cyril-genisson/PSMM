#!/usr/bin/env bash
PUBKEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDzzWvUju35pLVFup57wookj1FSOp2x6P16wIWFJmG9t monitor@laplateforme.lan"
USERNAME=monitor
PUBLIC=eth0
PRIVATE=eth1

if id -u $USERNAME >/dev/null 2>&1; then
    echo "L'utilisateur '$USERNAME' existe déjà." 
else
    useradd -m -c $USERNAME -G sudo,systemd-journal -s /bin/bash $USERNAME
    echo "$USERNAME:$USERNAME" | chpasswd
    echo "L'utilisateur '$USERNAME' a été créé avec succès."
    echo  "$USERNAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USERNAME
    chmod 440 /etc/sudoers.d/$USERNAME
    mkdir /home/$USERNAME/.ssh
    chmod 700 /home/$USERNAME/.ssh
    chown $USERNAME:$USERNAME /home/$USERNAME/.ssh
    echo $PUBKEY > /home/$USERNAME/.ssh/authorized_keys
    chmod 600 /home/$USERNAME/.ssh/authorized_keys
    chown $USERNAME:$USERNAME /home/$USERNAME/.ssh/authorized_keys

    echo "192.168.200.10 psmm.laplateforme.lan psmm" >> /etc/hosts
    echo "192.168.200.11 web.laplateforme.lan web" >> /etc/hosts
    echo "192.168.200.12 db.laplateforme.lan db" >> /etc/hosts
    echo "192.168.200.13 ftp.laplateforme.lan ftp" >> /etc/hosts

    apt update
    apt install -y vim bash-completion firewalld curl lftp

    firewall-cmd --permanent --zone=public --change-interface=eth0
    firewall-cmd --permanent --zone=public --change-interface=eth1
    firewall-cmd --reload
fi
