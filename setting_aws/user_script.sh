#!/bin/bash

# git clone 시에 root path에 실행하게 되므로 ec2-user home dirtory로 이동
sudo yum install -y git && \
sudo amazon-linux-extras install -y ansible2 && \
cd /home/ec2-user && \
sudo -u ec2-user git clone https://github.com/ehdrn3020/kafka_system_with_azar.git