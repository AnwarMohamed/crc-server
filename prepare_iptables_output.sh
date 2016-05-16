#!/bin/bash

iptables -F OUTPUT
# allow root
iptables -A OUTPUT  -m owner  --gid-owner root  -j ACCEPT
#iptables -A OUTPUT  -m owner  --gid-owner 0:501  -j ACCEPT
#iptables -A OUTPUT  -m owner  --gid-owner 65534  -j ACCEPT

iptables -A OUTPUT -m owner ! --gid-owner 500 -j ACCEPT

#iptables -A OUTPUT  -m owner  --uid-owner nobody  -j ACCEPT
#iptables -A OUTPUT -m pkttype --pkt-type multicast -j ACCEPT

# create user group filter
iptables -F USERS_NODES_FILTER 
iptables -N USERS_NODES_FILTER 
iptables -A OUTPUT  -j USERS_NODES_FILTER -o eth1

iptables -A OUTPUT  -o eth1   -j REJECT

crcUsers=$(members crc-users)

for usr in $crcUsers; do
    iptables -N $usr
    iptables -A USERS_NODES_FILTER  -j $usr -m owner   --uid-owner $usr
done
