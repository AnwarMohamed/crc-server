#!/bin/bash

iptables -F OUTPUT
# allow root
iptables -A OUTPUT  -m owner  --gid-owner root  -j ACCEPT
#iptables -A OUTPUT  -m owner  --gid-owner 0:501  -j ACCEPT
#iptables -A OUTPUT  -m owner  --gid-owner 65534  -j ACCEPT

iptables -A OUTPUT -m owner ! --gid-owner 502:10000 -j ACCEPT

#iptables -A OUTPUT  -m owner  --uid-owner nobody  -j ACCEPT
#iptables -A OUTPUT -m pkttype --pkt-type multicast -j ACCEPT

# create user group filter
iptables -N USERS_NODES_FILTER 
iptables -A OUTPUT  -j USERS_NODES_FILTER -o br0

iptables -A OUTPUT  -o br0   -j REJECT

