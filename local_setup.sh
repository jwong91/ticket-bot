#!/bin/bash

# Copy project to remote machine
scp -r ./* $1:~/twitter-bot

# SSH into remote machine and run setup script
ssh $1 'bash -s' < ./remote_setup.sh
