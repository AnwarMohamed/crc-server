#!/bin/bash
#arguments are: nodeList imageName
set -x #-e
LOG=""


echo "[`date`] INFO: Starting omf_laod.sh" >> $LOG
TASKS_DIR=/usr/local/share/frisbee_tasks
DNSMASQ_PATH=/etc/dnsmasq.d/testbed.conf


if [[ $1 == "" ]]  ; then
	echo "Usage: ./revoke_user_nodes.sh  username"
	exit -1
fi


USER_NAME=$1

user_exists=$(id -u $USER_NAME ) 
if  [ -z "$user_exists" ]; then
    exit -1
fi


iptables -F $USER_NAME 
				
