#!/bin/bash

# this script runs the homek8s provisioning against the virtual cluster.
# native_run_machines.sh must be run before this script.
# local_build.sh must be run before this script (or the docker hub image is used).

# switch to scriptdir
OLD_PWD="$(pwd)"
cd "$(dirname "$0")"


# run default site.yml playbook to provision a homek8s cluster to the qemu VMs.
# we use --network host so that the docker container can access the gateway VM's ssh port via localhost:5022
docker run -it --rm --network host -v $(pwd)/hosts.qemu:/etc/ansible/hosts homek8s/homek8s