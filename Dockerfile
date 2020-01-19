FROM debian:buster

WORKDIR /etc/ansible

RUN apt-get update && apt-get install -y \
    ansible python3-apt openssh-client \
 && rm -rf /var/lib/apt/lists/*

 COPY roles /etc/ansible/roles
 COPY playbooks /etc/ansible/playbooks

 ENTRYPOINT [ "ansible-playbook" ]
 CMD [ "playbooks/site.yml" ]