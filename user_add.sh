#!/bin/bash
if [[ $1 == "" ]] | [[ $2 == "" ]]; then
    echo "Usage: ./user_add.sh username password"
    exit
fi

ret=false
getent passwd $1 >/dev/null 2>&1 && ret=true

if $ret; then
    echo "User Exists"
else
    useradd -g crc-users -m $1
    echo "$2:$1" | chpasswd

fi
