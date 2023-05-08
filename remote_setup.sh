#!/bin/bash

# Install dependencies
cd /home/jtwong2/ticket-bot/
sudo apt-get install -y python3-pip
sudo pip3 install -r requirements.txt

# Launch bot
cd /home/jtwong2/ticket-bot/bots/
pwd
python3 twitter_bot.py
