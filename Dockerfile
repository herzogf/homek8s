FROM debian:buster

WORKDIR /etc/ansible

RUN apt-get update && apt-get install -y \
    ansible \
 && rm -rf /var/lib/apt/lists/*

 ENTRYPOINT [ "ansible-playbook" ]