#!bin/bash

# Install dependencies
sudo apt-get install python3-pip
sudo pip3 install -r requirements.txt

# Launch bot
python3 ticket-bot/bots/twitter_bot.py
