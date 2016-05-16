#!/bin/bash
#arguments are: nodeList imageName
set -x #-e

DNSMASQ_PATH=/etc/dnsmasq.d/testbed.conf


if [[ $1 == "" ]]  || [[ $2 == "" ]]  ; then
	echo "Usage: ./grant_user_nodes.sh  username node_names"
	exit -1
fi


USER_NAME=$1

user_exists=$(id -u $USER_NAME ) 
if  [ -z "$user_exists" ]; then
    exit -1
fi

NODES_STR=$2       # comma separated string of nodes on which we need to load images
IFS=',' read -ra NODES <<< "$NODES_STR"

INDEX=0
for i in "${NODES[@]}"; do
	RECORDS[$INDEX]=`cat $DNSMASQ_PATH | grep ,"$i",` # omf.crc.
	if [ -z "${RECORDS[$INDEX]}" ]; then
	for i in "${IDS[@]}"; do
    		echo "ERROR: Cannot find node with the name ${NODES[$INDEX]}" >> "tasks/$i-load.error"
	done
	  exit -1
	fi
	IPADDRS[$INDEX]=`echo ${RECORDS[$INDEX]} | cut -d , -f 4`
	INDEX=$INDEX+1
done


iptables -F $USER_NAME 

for i in "${IPADDRS[@]}"; do
	iptables -A $USER_NAME  -d $i  -j ACCEPT 	
	INDEX=$INDEX+1					
done							
