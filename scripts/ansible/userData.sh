#!/bin/bash
sudo amazon-linux-extras enable ansible2
sudo yum clean metadata
sudo yum install -y ansible git 

cd /tmp
sudo curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/linux_64bit/session-manager-plugin.rpm" -o "session-manager-plugin.rpm"
sudo yum install -y session-manager-plugin.rpm

# aws cli config
mkdir ~/.aws
touch ~/.aws/config
echo '[default]' >> ~/.aws/config
echo 'region = us-east-1' >> ~/.aws/config

# get ssh key for ansible
sudo aws ssm get-parameter --name pem-aws-study --query Parameter.Value --output text > /root/.ssh/aws-generl.pem
sudo chmod 400 /root/.ssh/aws-generl.pem

# ansible
mkdir /opt/ansible

echo glpat-6pnkeDozoaBeakg-5KMq