#!/bin/bash

# this script starts the master with pxe for the installation.
# you should use this only for the first boot, after the initial installation
# please use the script native_run_master_run.sh to boot it from disk

# switch to scriptdir
OLD_PWD="$(pwd)"
cd "$(dirname "$0")"

rm -f tmp/master.qcow2
qemu-img create -f qcow2 tmp/master.qcow2 32G

kvm -m 1024 -smp 2 \
  -boot n \
  -hda tmp/master.qcow2 \
  -option-rom /usr/share/qemu/pxe-rtl8139.rom \
  -net nic,vlan=1,macaddr=FA:2D:37:78:7F:CF -net socket,vlan=1,mcast=230.0.0.1:1234

# login in this console with user pi / password raspberry
# or
# login via "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 5022 pi@localhost"

cd "$OLD_PWD"