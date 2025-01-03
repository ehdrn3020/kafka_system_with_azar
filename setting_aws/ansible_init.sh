#!/bin/bash
echo "Starting SSH agent..."
ssh-agent bash
ssh-add keypair.pem
ssh-keygen -t rsa -b 4096 -f /home/ec2-user/.ssh/id_rsa -N "" -q
cat /home/ec2-user/.ssh/id_rsa.pub >> /home/ec2-user/.ssh/authorized_keys
cat /home/ec2-user/.ssh/id_rsa.pub
cat /home/ec2-user/.ssh/authorized_keys

echo "Ansible Init"
cd /home/ec2-user/kafka_system_with_azar/ansible
git pull
ansible-playbook -i inventory/hosts init.yml