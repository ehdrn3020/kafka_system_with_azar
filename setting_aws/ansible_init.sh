#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define variables
PRIVATE_KEY="keypair.pem"
SSH_DIR="/home/ec2-user/.ssh"
ID_RSA="$SSH_DIR/id_rsa"
AUTHORIZED_KEYS="$SSH_DIR/authorized_keys"
GIT_REPO_PATH="/path/to/your/repo"  # Git repository path
ANSIBLE_PLAYBOOK="init.yml"

# Start SSH agent
echo "Starting SSH agent..."
eval "$(ssh-agent -s)"

# Add private key to SSH agent
if [[ -f $PRIVATE_KEY ]]; then
    echo "Adding private key to SSH agent..."
    ssh-add $PRIVATE_KEY
else
    echo "Private key file $PRIVATE_KEY not found!"
    exit 1
fi

# Ensure .ssh directory exists
echo "Ensuring $SSH_DIR exists..."
mkdir -p $SSH_DIR
chmod 700 $SSH_DIR
chown ec2-user:ec2-user $SSH_DIR

# Generate SSH key pair if not exists
if [[ ! -f $ID_RSA ]]; then
    echo "Generating SSH key pair..."
    ssh-keygen -t rsa -b 4096 -f $ID_RSA -N "" -q
else
    echo "SSH key pair already exists at $ID_RSA."
fi

# Add public key to authorized_keys
if [[ -f $ID_RSA.pub ]]; then
    echo "Adding public key to authorized_keys..."
    cat $ID_RSA.pub >> $AUTHORIZED_KEYS
    sort -u $AUTHORIZED_KEYS -o $AUTHORIZED_KEYS # Remove duplicates
    chmod 600 $AUTHORIZED_KEYS
    chown ec2-user:ec2-user $AUTHORIZED_KEYS
else
    echo "Public key $ID_RSA.pub not found!"
    exit 1
fi

# Navigate to Git repository and pull latest changes
if [[ -d $GIT_REPO_PATH ]]; then
    echo "Navigating to Git repository and pulling latest changes..."
    cd $GIT_REPO_PATH
    git pull
else
    echo "Git repository path $GIT_REPO_PATH not found!"
    exit 1
fi

# Run Ansible playbook
echo "Running Ansible playbook..."
ansible-playbook -i inventory/hosts $ANSIBLE_PLAYBOOK

echo "Setup and deployment complete."
