#!/bin/bash
if [[ $1 == "" ]] | [[ $2 == "" ]]; then
    echo "Usage: ./user_add.sh username password"
    exit
fi

ret=false
getent passwd $1 >/dev/null 2>&1 && ret=true

if $ret; then
    echo "User Exists" >/dev/null 2>&1
else
    mkdir -p /home/crc-users/$1 
    useradd -g crc-users -m -s /bin/bash -d /home/crc-users/$1  $1 
    echo "$1:$2" | chpasswd
    cp -v /etc/skel/.bash* /home/crc-users/$1   
    
    # create group for user
    groupadd $1 
    usermod -aG $1 $1 
    # create iptable chain for user
    iptables -N $1 -m owner   --gid-owner $1
    iptables -A USERS_NODES_FILTER  -j $1

fi
