#!/bin/bash
if [[ $1 == "" ]] ; then
    echo "Usage: ./user_delete.sh username"
    exit
fi

if groups $1 | grep "crc-users"; then
    groupdel $1
    userdel -f -r $1 >& /dev/null
    iptables -F $1
    iptables -D USERS_NODES_FILTER -j $1
    iptables -X $1
     
else
   echo "User not deleted or not found"
fi
