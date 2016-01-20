#!/bin/bash
if [[ $1 == "" ]] ; then
    echo "Usage: ./user_delete.sh username"
    exit
fi

if groups $1 | grep "crc-users"; then
    userdel -f -r $1 >& /dev/null
else
   echo "User not deleted or not found"
fi
