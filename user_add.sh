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
    echo "$2:$1" | chpasswd
fi
