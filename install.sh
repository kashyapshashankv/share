#!/bin/sh
yum install epel-release -y
yum install ansible -y
yum install -y yum-utils
yum install -y rust
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install docker-ce docker-ce-cli containerd.io -y
systemctl start docker
systemctl enable docker
yum install wget -y
yum install unzip -y
yum install -y python3
yum install -y python
pip3 install docker-compose
mkdir /var/lib/pgdocker
wget https://github.com/ansible/awx/archive/refs/tags/15.0.1.zip
unzip 15.0.1.zip -d awx
cd awx/awx-15.0.1/installer  
mv inventory invetory_old
echo 'localhost ansible_connection=local ansible_python_interpreter="/usr/bin/env python3"

[all:vars]
create_preload_data=False
dockerhub_base=ansible
project_data_dir=/var/lib/awx/projects
awx_task_hostname=awx
awx_web_hostname=awxweb
postgres_data_dir="/var/lib/pgdocker"
host_port=80
host_port_ssl=443
docker_compose_dir="~/.awx/awxcompose"
pg_username=awx
pg_password=awxpass
pg_database=awx
pg_port=5432
pg_admin_password=password
rabbitmq_password=awxpass
rabbitmq_erlang_cookie=cookiemonster
admin_user=admin
admin_password=password
secret_key=R+kbcDEUS8DlAftAbfWafVqLZ0lUy+Paqo4fEtgp
awx_alternate_dns_servers="8.8.8.8,8.8.4.4"
'>> inventory

ansible-playbook -i inventory install.yml