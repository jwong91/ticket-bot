#!/bin/bash

# SSH into remote machine and clone code
ssh jtwong2@$1 'git clone https://github.com/jwong91/ticket-bot.git'

# Copy secrets to remote machine
scp -r ./secrets.json jtwong2@$1:~/ticket-bot/

# SSH into remote machine and run setup script
ssh jtwong2@$1 'bash -s' < ./remote_setup.sh
