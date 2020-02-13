FROM debian:buster

WORKDIR /etc/ansible

RUN \
  apt-get update && \
  apt-get install -y gnupg python3-apt openssh-client sshpass rsync && \
  echo "deb http://ppa.launchpad.net/ansible/ansible/ubuntu bionic main" >> /etc/apt/sources.list && \
  apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367 && \
  apt-get update && \
  apt-get install -y ansible && \
  rm -rf /var/lib/apt/lists/* && \
  mkdir /homek8s

 COPY roles /etc/ansible/roles
 COPY playbooks /etc/ansible/playbooks

 ENTRYPOINT [ "ansible-playbook", "-i", "/homek8s/hosts" ]
 CMD [ "playbooks/site.yml" ]