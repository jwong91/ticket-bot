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

MIN_ADVANCE_DAYS = 7 # days
class TwitterBot():
    def decide_purchase(self, show_date, min_days_in_advance=MIN_ADVANCE_DAYS):
        if show_date == date(2023, 5, 28): # Prefer Metlife tickets
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
            print("[ERROR]: secrets.json not found (" + str(e) + ")")
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
        # time.sleep(2)

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
        user_acc = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[2]/div/div/div/form/div[2]/div/div[2]/div")
        ActionChains(self.driver)\
        .double_click(user_acc)\
        .perform()
        self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[1]/div/div/div/div/div/div[3]/div/div/div/span/span").click()
        time.sleep(0.5)
        message_bar = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/main/div/div/div/section[2]/div/div/div[2]/div/div/aside/div[2]/div[2]/div/div/div/div/div/label/div[1]/div/div/div/div/div/div[2]/div/div/div/div").click()
        # ActionChains(self.driver)\
        # .click(message_bar)\
        # .perform()
        time.sleep(1)

        # self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/main/div/div/div/section[2]/div/div/div[2]/div/div/aside/div[2]/div[2]/div/div/div/div/div/label/div[1]/div/div/div/div/div/div[2]/div/div/div/div").send_keys("hi utahzen")
        TwitterBot.slow_type(self, message)
        self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/main/div/div/div/section[2]/div/div/div[2]/div/div/aside/div[2]/div[3]/div").click()

    def get_tickets(self, message_content):
        # self.driver = webdriver.Firefox(service=Service(gecko().install()))

        # config options and open browser
        options = FirefoxOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options, service=Service(gecko().install()))

        TwitterBot.twitter_login(self)
        self.driver.implicitly_wait(8)

        print("\nItem: " + message_content)
        location = re.search(r"show in.*?/", message_content).group().replace("show in", "").replace("on", "")[:-2].rstrip().lstrip()
        print("\nLocation: \"" + location + "\"") # it was a syntax error on using match()
        price = re.search(r"Selling for \$(\d+) ", message_content).group().replace("Selling for ", "").rstrip().lstrip()
        print("Price: " + price)
        quantity = re.search(r"[(](\d+)[)]", message_content).group().replace("(", "").replace(")", "")
        print("Quantity: " + quantity)
        seller_username = re.search(r"DM *@[A-Za-z0-9_]+", message_content).group().replace("DM", "").replace("@", "").lstrip().rstrip()
        print("Seller: " + seller_username)
        event_date = re.search(r"(\d+/\d+)", message_content).group()
        print("Date: " + event_date)

        # Determine if the event is far enough into the future
        shouldPurchase = self.decide_purchase(date(2023, int(event_date.split("/")[0]), int(event_date.split("/")[1])))

        # Write to log file
        stats = "\nLocation: " + location + "\nPrice: " + price + "\nQuantity: " + quantity + "\nSeller: " + seller_username + "\nDate: " + event_date + "\nShould purchase: " + str(shouldPurchase)
        with open("../logs/twitterhistory.log", "a") as f:
            f.write("\n\n[" + str(datetime.now().time().hour) + ":" + str(datetime.now().time().minute) + ":" + str(datetime.now().time().second) + "]:" + stats)

        with open("dm_list.txt", "r") as f:
            dm_list = f.read().splitlines()
            if seller_username in dm_list or not shouldPurchase:
                print("[WARN] Already messaged this user")
            else:
                message = "Hey there! I'm interested in your Taylor Swift tickets. I'm willing to pay the listed price for them. Please let me know if you're interested. Thanks!"
                self.access_messages("utahzen", message + stats)

        with open("dm_list.txt", "a") as f:
            f.write(seller_username + "\n")

        time.sleep(5)
        self.driver.close()
        return stats


    def main(self):
        try:
            with open("../secrets.json") as f:
               data = json.load(f)
               token = data["bot-token"]["token"]
        except Exception as e:
            print("[ERROR]: secrets.json not found (" + str(e) + ")")
            return

        client = discord.Client()

        @client.event
        async def on_ready():
            print('we have logged in as {0.user}'.format(client))

        @client.event
        async def on_message(message):
            if (message.author.id == 832731781231804447 or message.author.id == 362779255634919424) and not "I'm " in message.content: # IFTTT Bot or me
                await message.channel.send("getting twitter tickets...")
                await message.channel.send(self.get_tickets(message.content))
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