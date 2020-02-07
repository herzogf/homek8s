#!/bin/bash

# this script installs all dependencies and prerequirements to run
# raspbian natively with qemu (i.e. as a VM directly on the host, not within a docker container)

# fail fast
set -e

# switch to scriptdir
OLD_PWD="$(pwd)"
cd "$(dirname "$0")"

# Installs the dependencies required to run a virtual homek8s cluster on x86 debian based linux
sudo apt-get install qemu qemu-system-arm kpartx

# Prepate tmp dir
rm -rf tmp
mkdir -p tmp
cd tmp

# Download raspberry pi image
wget -O raspbian_lite_latest.zip https://downloads.raspberrypi.org/raspbian_lite_latest
unzip raspbian_lite_latest.zip
rm -f raspbian_lite_latest.zip
ln -s *.img raspbian_lite_latest.img
#qemu-img resize raspbian_lite_latest.img +10G

# make some modifications to the raspbian image for homek8s
bootLoopDevice="$(sudo kpartx -avs raspbian_lite_latest.img | head -n 1 | awk '{print $3}')"
# add ssh file to boot partition to activate ssh directly during raspbian start
mkdir boot
sudo mount -o loop "/dev/mapper/${bootLoopDevice}" boot
sudo touch boot/ssh
sudo umount boot
# FIXME: change raspi hostname to rpi-gateway
sudo kpartx -d raspbian_lite_latest.img

# Download qemu-optimized raspberry pi kernel
git clone https://github.com/dhruvvyas90/qemu-rpi-kernel.git

cd "$OLD_PWD"


# links:
# https://github.com/dhruvvyas90/qemu-rpi-kernel
# https://github.com/lukechilds/dockerpi/