#!/bin/bash

# Install dependencies
sudo apt-get install -y python3-pip
sudo pip3 install -r requirements.txt

# Launch bot
python3 bots/twitter_bot.py
