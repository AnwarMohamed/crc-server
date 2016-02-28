#!/bin/bash
set -x #-e
LOG="Frisbee.log"
#Initial state of the target machine when using this script: ON, ubuntu
#########################################
#            PREPARATION                #
#########################################
TASKS_DIR=/usr/local/share/frisbee_tasks
DNSMASQ_PATH=/etc/dnsmasq.d/testbed.conf
PXEDIR=/tftpboot/pxelinux.cfg
PXECONF=$PXEDIR/tinycore
STORAGEDIRECTORY=/usr/local/share/storage

COREUSER=root
COREPASS=masterpassword

if [[ $1 == "" ]]  || [[ $2 == "" ]] || [[ $3 == "" ]] ; then
	echo "Usage: ./omf_save.sh node_name image_name task_id"
	exit
fi

NODE=$1        # constructed from command line parameters
IMAGENAME=$2   # constructed from command line parameters
ID=$3
ERROR="$TASKS_DIR/$ID-save.error"
PROGRESS="$TASKS_DIR/$ID-save.progress"
CLIENT_LOG="$NODE-$IMAGENAME-save.log"
#First time to use the file, overwrite
echo "" > $CLIENT_LOG

echo "Saving image on $NODE with name $IMAGENAME to the storage server"
RECORD=`cat $DNSMASQ_PATH | grep ,"$NODE",` # omf.crc.
#Check if this record exists
if [ -z "$RECORD" ]; then
    echo "ERROR: Cannot find node with the given name" >> $ERROR
fi

IPADDR=`echo "$RECORD" | cut -d , -f 4`
MACADDR=`echo "$RECORD" | cut -d , -f 2 | tr '[:upper:]' '[:lower:]'`
PXELINK=$PXEDIR/01-`echo "$MACADDR" | sed 's/:/-/g'`
echo "[`date`] INFO: OMF Save Preparation phase finished" >> $LOG
echo "[`date`] INFO: Image on $NODE will be saved to the storage server with name $IMAGENAME" >> $LOG
echo "[`date`] INFO: Image Saving starts" >> $PROGRESS
echo "[`date`] INFO: Creating symbolic link with name $MACADDR" >> $LOG
sudo rm -rf $PXELINK
sudo ln -sv $PXECONF $PXELINK
echo "[`date`] INFO: Restarting $NODE" >> $LOG
echo "[`date`] INFO: after expected line" >> $LOG
	RETURN=$(curl --write-out %{http_code} --write-out %{http_code} --silent --output /dev/null -data=""  http://193.227.16.154:7777/api/v1/vm/$NODE/reset2)
	if [ "$RETURN" -ne 200 ] ; then
		echo "Restart from VM failed! Try to access the node itself"
		ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null crc@$IPADDR \
        		"sudo -S shutdown -r now"
		RETURN=$?
		if [ "$RETURN" -ne 0 ] ; then
		  echo "Error Can't ssh on $NODE to restart ubuntu" >> $CLIENT_LOG
		  echo "ERROR: Cannot access $NODE to restart" >> $ERROR
		fi
	fi
sleep 15
response=$(nc -zv $NODE 22; echo $?)
while [[ "$response" -ne 0 ]]
do 
  echo "Response is $response#################################"
  echo "Waiting for 1 second for $NODE to restart....."
  sleep 1
  response=$(nc -zv $NODE 22; echo $?) #0: succeeded, 1: not
done
#Check that this node is ON and reachable
#==============================================
RES=`ping -c 1 -t 10 $IPADDR ; echo $?`
i=$((${#RES}-1))
LAST=${RES:$i:1}
if [ $LAST == "0" ];
then
  echo "$NODE is running and reachable"
  echo "[`date`] INFO: $NODE is running and reachable" >> $LOG
else
  echo "$NODE is unreachable. Check that it is ON and connected properly to the network"
  echo "[`date`] INFO: $NODE is unreachable. Check that it is ON and connected properly to the network" >> $LOG
  echo "ERROR: $NODE is unreachable on the network" >> $ERROR
  exit -1
fi
#==============================================
#echo "[`date`] INFO: Starting imagezip on $NODE after 10 seconds" >> $PROGRESS
#sleep 10 
echo "[`date`] INFO: Starting imagezip on $NODE" >> $LOG
echo "imagezip is starting..."
#TODO: Check if imagezip produces some errors which are required to be passed to the error file!
sshpass -p $COREPASS ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $COREUSER@$IPADDR \
        "imagezip -l /dev/sda1 -" > $STORAGEDIRECTORY/"${IMAGENAME}_$NODE.ndz"
RETURN=$?
if [ "$RETURN" -ne 0 ] ; then
	echo "ERROR: Cannot save image on $NODE" >> $ERROR
	echo "Error Can't ssh on $NODE to run imagezip on it" >> $CLIENT_LOG
fi
sudo rm -rf $PXELINK #To restart on ubuntu the next time, we have to remove the PXE symbolic link
echo "[`date`] INFO: Image of $NODE is saved with name ${IMAGENAME}_$NODE on storage server" >> $LOG
echo "imagezip is done"
echo "Save DONE!" >> $PROGRESS
