#!/bin/bash

# allow root
 iptables -A OUTPUT  -m owner  -o br0  --gid-owner 0  -j ACCEPT

# create user group filter
iptables -N USERS_NODES_FILTER 
iptables -A OUTPUT  -j USERS_NODES_FILTER -o br0

iptables -A OUTPUT  -o br0   -j REJECT

