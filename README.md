# homek8s
Kubernetes installer for your datacenter at home.

## Work in progress
Does nothing useful at the moment :-)

Sample start command:
```bash
# create local homek8s directory containing the ansible inventory file "hosts".
# also used by the ansible playbooks for writing cluster metadata in it, e.g generated ssh keys
mkdir -p my_homek8s ; cd my_homek8s

# copy sample inventory file and edit for your home network
cp ../inventory/hosts.example hosts ; vi hosts

# dry-run
docker run -it --rm -v $(pwd):/homek8s -v ${HOME}/.ssh:/root/.ssh homek8s/homek8s playbooks/site.yml --check -vvv
# run site.yml playbook
docker run -it --rm -v $(pwd):/homek8s -v ${HOME}/.ssh:/root/.ssh homek8s/homek8s
```

## Testing
To speed up development and testing we can start a virtual test environment locally, consisting of
* a virtual machine with arm architecture (sort of fake raspberry pi) with raspian for the gateway
* x86 virtual machines for the k8s master and nodes (not implemented yet)

To test locally on a current debian based linux system run the following commands:
```bash
# builds the homek8s docker image
./local_build.sh

# installs qemu, downloads raspbian and needed custom raspi kernels
./test/native_install_prereqs.sh

# starts the raspbian / gateway with qemu
# -> at the moment this blocks the shell session and shows the gateway VM's console
./test/native_run_gateway.sh

# in a new shell session:
# start homek8s targeting the virtual machines
./test/native_run_homek8s.sh
```