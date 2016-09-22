#!/bin/bash
set -x #-e



if [[ $1 == "" ]]  || [[ $2 == "" ]] || [[ $3 == "" ]] || [[ $4 == "" ]]  ; then
	echo "Usage: ./grant_user_nodes_timeslot.sh  username node_names start_date_time  end_date_time"
	echo "Date format is HH:MM CCYY-MM-DD"
        exit -1
fi


user_name=$1;
node_names=$2;
start_date_time=$3;
end_date_time=$4;


grant_script="/home/crc-admin/crc-server/grant_user_nodes.sh"
revoke_script="/home/crc-admin/crc-server/revoke_user_all_nodes.sh"

let diff=(`date +%s -d "$start_date_time"`-`date +%s`); echo $diff
   if [[ diff -gt "0" ]]; then
   echo "Start Date is in the future"
   echo "$grant_script  $user_name $node_names"   | at "$start_date_time";
else
   echo "Start Date is in the past"
  if [[ diff -lt "-3600" ]]; then
      echo "Somethig is wrong date is too far in the past"
  else
    `$grant_script  $user_name $node_names`
  fi 
fi


echo "$revoke_script  $user_name" | at "$end_date_time" 
