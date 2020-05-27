#!/bin/bash

# this script starts the master from disk.
# please run native_run_master_install.sh first (only one time needed)

# switch to scriptdir
OLD_PWD="$(pwd)"
cd "$(dirname "$0")"

kvm -m 1024 -smp 2 \
  -hda tmp/node.qcow2 \
  -net nic,vlan=1,macaddr=22:18:ce:b4:4c:cd -net socket,vlan=1,mcast=230.0.0.1:1234 \
  -nographic \
  --serial mon:stdio
  #-curses \

# login in this console with user pi / password raspberry
# or
# login via "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 5022 pi@localhost"

cd "$OLD_PWD"