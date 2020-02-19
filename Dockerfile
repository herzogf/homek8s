FROM debian:buster

WORKDIR /etc/ansible

RUN \
  apt-get update && \
  apt-get install -y gnupg python3-apt openssh-client sshpass rsync git && \
  echo "deb http://ppa.launchpad.net/ansible/ansible/ubuntu bionic main" >> /etc/apt/sources.list && \
  apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367 && \
  apt-get update && \
  apt-get install -y ansible && \
  rm -rf /var/lib/apt/lists/* && \
  mkdir /tmp/k3s-git && git clone --depth 1 https://github.com/rancher/k3s.git --branch master /tmp/k3s-git && \
  cp -pr /tmp/k3s-git/contrib/ansible/roles /tmp/ && rm -rf /tmp/k3s-git && \
  mkdir /homek8s

 COPY roles /etc/ansible/roles
 COPY playbooks /etc/ansible/playbooks

 # add all ansible playbooks & roles (homek8s & k3s) to a tar.gz which is then copied to the gateway
 RUN \
  cp -pr /etc/ansible/roles/* /tmp/roles/ && \
  cp -pr /etc/ansible/roles/gateway/files/node_provisioning/playbooks /tmp/ && \
  mv /tmp/roles /tmp/playbooks && \
  tar -czf /tmp/gateway-ansible.tar.gz -C /tmp/ playbooks && \
  rm -rf /tmp/playbooks

 ENTRYPOINT [ "ansible-playbook", "-i", "/homek8s/hosts" ]
 CMD [ "playbooks/site.yml" ]