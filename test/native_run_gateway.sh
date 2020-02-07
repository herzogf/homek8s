#!/bin/bash

# this script starts the gateway, i.e. a qemu VM with raspbian.
# native_install_prereqs.sh must be run before this script.

# switch to scriptdir
OLD_PWD="$(pwd)"
cd "$(dirname "$0")"

qemu-system-arm \
  -M versatilepb \
  -cpu arm1176 \
  -m 256 \
  -net nic,vlan=0 -net user,vlan=0,hostfwd=tcp::5022-:22 \
  -net nic,vlan=1,model=virtio -net socket,vlan=1,mcast=230.0.0.1:1234 \
  -hda tmp/raspbian_lite_latest.img \
  -dtb tmp/qemu-rpi-kernel/versatile-pb.dtb \
  -kernel tmp/qemu-rpi-kernel/kernel-qemu-*-buster \
  -append 'root=/dev/sda2 panic=1' \
  -no-reboot \
  --display none \
  --serial mon:stdio

# login in this console with user pi / password raspberry
# or
# login via "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 5022 pi@localhost"

cd "$OLD_PWD"