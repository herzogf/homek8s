# homek8s
Kubernetes installer for your datacenter at home.

## Work in progress
Does nothing useful at the moment :-)

Sample start command:
```bash
#dry-run
docker run -it --rm -v $(pwd)/hosts:/etc/ansible/hosts -v ${HOME}/.ssh:/root/.ssh homek8s/homek8s playbooks/site.yml --check -vvv
#run site.yml playbook
docker run -it --rm -v $(pwd)/hosts:/etc/ansible/hosts -v ${HOME}/.ssh:/root/.ssh homek8s/homek8s
```