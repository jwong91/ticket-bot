from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common import by
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager as gecko
import discord
from discord import Intents

from datetime import datetime, date, timedelta
import sys
import re
import time
import random
import json
from enum import Enum

MIN_ADVANCE_DAYS = 7 # days

class WarnLevel(Enum):
    INFO = 1
    WARN = 2
    ERROR = 3
class TwitterBot():
    def decide_purchase(self, show_date, min_days_in_advance=MIN_ADVANCE_DAYS):
        if show_date == date(2023, 5, 28): # Prefer Metlife tickets
            self.log("Metlife show found, purchasing", WarnLevel.INFO)
            return True

        current_date = date.today()
        min_day = current_date + timedelta(days=min_days_in_advance)
        return show_date >= min_day

    def twitter_login(self):
        try:
            with open("../secrets.json") as f:
               data = json.load(f)
               user = data["twitter"]["user"]
               pw = data["twitter"]["pw"]
        except Exception as e:
            self.log("secrets.json not found (" + str(e) + ")", WarnLevel.ERROR)
            return

        self.driver.get("https://twitter.com/ErasTourResell")
        self.driver.implicitly_wait(5)
        login_button = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div/div[1]/div/div/div/div[2]/div[2]/div/div/div[1]/a/div")
        login_button.click()
        login_field = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input")
        login_field.send_keys(user)
        username_submit_button = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div")
        username_submit_button.click()
        password_field = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input")
        password_field.send_keys(pw)
        password_submit_button = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div")
        password_submit_button.click()
        time.sleep(1)
        self.driver.get("https://twitter.com/ErasTourResell")

    def slow_type(self, text, delay=0.0):
        # Send a text to an element one character at a time with a delay.
        for c in text:
            if c == "\n":
                ActionChains(self.driver)\
                .key_down(Keys.SHIFT)\
                .send_keys(Keys.RETURN)\
                .key_up(Keys.SHIFT)\
                .perform()
            else:
                ActionChains(self.driver)\
                .send_keys(c)\
                .perform()
            time.sleep(delay)

    def access_messages(self, recipient, message):
        self.driver.get("https://twitter.com/messages/compose")
        self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input").send_keys("@" + recipient)
        ActionChains(self.driver)\
        .send_keys("\ue007")\
        .perform()
        time.sleep(1)
        # Check to see if the user is the correct one
        user_name = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/form/div[2]/div/div[2]/div/div/div/div[2]/div[1]/div/div/div[2]/div/div/div/span").text[1:]
        if user_name != recipient:
            self.log("User " + recipient + " not found (did not come up first in the search bar)", WarnLevel.ERROR)
            return

        user_acc = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/form/div[2]/div/div[2]/div")
        ActionChains(self.driver)\
        .double_click(user_acc)\
        .perform()
        self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/div[3]/div/div/div/span/span").click()
        time.sleep(0.5)
        self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/main/div/div/div/section[2]/div/div/div[2]/div/div/aside/div[2]/div[2]/div/div/div/div/div/label/div[1]/div/div/div/div/div/div[2]/div/div/div/div").click()
        time.sleep(1)

        TwitterBot.slow_type(self, message)
        # self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/main/div/div/div/section[2]/div/div/div[2]/div/div/aside/div[2]/div[3]/div").click()
        input("waiting for supervisor confirmation...")

    def get_tickets(self, message_content):
        # config options and open browser
        options = FirefoxOptions()
        # options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options, service=Service(gecko().install()))
        # print(self.driver.)

        TwitterBot.twitter_login(self)
        self.driver.implicitly_wait(8)

        location = re.search(r"show in.*?/", message_content).group().replace("show in", "").replace("on", "")[:-2].rstrip().lstrip()
        price = re.search(r"Selling for \$(\d+) |Selling for \$(\d+).(\d+) ", message_content).group().replace("Selling for ", "").rstrip().lstrip()
        quantity = re.search(r"[(](\d+)[)]", message_content).group().replace("(", "").replace(")", "")
        seller_username = re.search(r"DM *@[A-Za-z0-9_]+", message_content).group().replace("DM", "").replace("@", "").lstrip().rstrip()
        event_date = re.search(r"(\d+/\d+)", message_content).group()

        # Determine if the event is far enough into the future
        shouldPurchase = self.decide_purchase(date(2023, int(event_date.split("/")[0]), int(event_date.split("/")[1])))

        # Log offer details
        stats = "\nLocation: " + location + "\nPrice: " + price + "\nQuantity: " + quantity + "\nSeller: " + seller_username + "\nDate: " + event_date + "\nShould purchase: " + str(shouldPurchase)
        self.log(stats, WarnLevel.INFO)

        # Decide whether to purchase or not (and purchase if so)
        with open("dm_list.txt", "r+") as f:
            dm_list = f.read().splitlines()
            if seller_username in dm_list or not shouldPurchase:
                self.log("Already messaged this user", WarnLevel.WARN)
            else:
                message = "Hey there! I'm interested in your Taylor Swift tickets. I'm willing to pay the listed price for them. Please let me know if you're interested. Thanks!"
                self.access_messages(seller_username, message + stats)
                self.log("Messaged user", WarnLevel.INFO)

        # Keep track of who has been messaged
        with open("dm_list.txt", "a+") as f:
            f.write(seller_username + "\n")

        self.driver.close()
        return stats

    def log(self, message, type):
        if type == WarnLevel.INFO:
            prefix = "INFO"
        elif type == WarnLevel.WARN:
            prefix = "WARN"
        elif type == WarnLevel.ERROR:
            prefix = "ERROR"

        with open("../logs/twitterhistory.log", "a+") as f:
            dt = datetime.now()
            msg = "\n\n[" + prefix + " " + format(dt, '%H') + ":" + format(dt, '%M') + ":" + format(dt, '%S') + "]: " + message
            f.write(msg)
            print(msg)

    def main(self):
        self.log("Starting Twitter Bot", WarnLevel.INFO)
        try:
            with open("../secrets.json") as f:
               data = json.load(f)
               token = data["bot-token"]["token"]
        except Exception as e:
            self.log("Secrets.json not found (" + str(e) + ")", WarnLevel.ERROR)
            return

        client = discord.Client()

        @client.event
        async def on_ready():
            print('we have logged in as {0.user}'.format(client))

        @client.event
        async def on_message(message):
            if (message.author.id == 832731781231804447 or message.author.id == 362779255634919424) and not "I'm " in message.content: # IFTTT Bot or me
                await message.channel.send("getting twitter tickets...")
                try:
                    await message.channel.send(self.get_tickets(message.content))
                except Exception as e:
                    self.log("Tweet did not include ticket information (" + e + ")", WarnLevel.INFO)
                    self.driver.close()
                return

            if message.content.startswith('tickets'):
                # while True:
                    await message.channel.send("getting twitter tickets...")
                    await message.channel.send(self.get_tickets())
                    fuzzy_time = random.randint(360, 460)
                    # time.sleep(fuzzy_time)

        client.run(token)

        self.driver.quit()

if __name__ == "__main__":
    bot = TwitterBot()
    bot.main()