from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver import FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager as gecko
from selenium.webdriver.common import by
import discord
from discord import Intents
from datetime import datetime
import sys
import re
import time
import random
import json

class TicketBot():
    def getMedian(self, prices):
        raw_prices = []
        for price in prices:
            if price.count(',') != 0:
                raw_prices.append(price[1:].replace(',', ''))

        raw_prices.sort()
        return raw_prices[len(raw_prices) // 2]

    def getAverage(self, prices):
        raw_prices = []
        for price in prices:
            if price.count(',') != 0:
                raw_prices.append(int(price[1:].replace(',', '')))

        return sum(raw_prices) / len(raw_prices)

    def minPrices(self, prices):
        raw_prices = []
        for price in prices:
            if price.count(',') != 0:
                raw_prices.append(int(price[1:].replace(',', '')))

        return min(raw_prices)

    def getTickets(self):
        driver = webdriver.Firefox(service=Service(gecko().install()))

        # config options and open browser
        options = FirefoxOptions()
        # self.driver = webdriver.Firefox(options=options)
        # driver2 = webdriver.Firefox(options=options)
        # driver3 = webdriver.Firefox(options=options)

        # determine which day to fetch
        dt = datetime.now()
        day = dt.weekday() # ranges from 0 (monday) to 6 (sunday)

        # normalize day to 2 (sunday) through 8 (saturday)
        day = (day + 1) % 7 # 0 (sunday) to 6 (saturday)
        day += 2 # 2 (sunday) to 8 (saturday)
        print(day)

        # try:
        driver.get("https://www.stubhub.com/taylor-swift-east-rutherford-tickets-5-28-2023/event/151197031/?quantity=2")
        driver.implicitly_wait(0.5)
        day_cell = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div/div[3]/div/div[2]/div/div")
        # m = re.match("$[0-9]+", day_cell.text)
        m = re.finditer(r"(\$(\d+)\,(\d+))|(\$(\d+))", day_cell.text)
        # m_prices = m.groups()
        prices = [match.group() for match in m]
        driver.close()
        stats = "\nMedian: $" + str(self.getMedian(prices)) + "\nAverage: $" + str(round(self.getAverage(prices), 2)) + "\nLowest: $" + str(self.minPrices(prices))
        with open("../logs/history.log", "a") as f:
            f.write("\n\n[" + str(datetime.now().time().hour) + ":" + str(datetime.now().time().minute) + ":" + str(datetime.now().time().second) + "]:" + stats)

        return "\n".join(prices) + stats

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
            if message.author.bot:
                return

            if message.content.startswith('tickets'):
                while True:
                    await message.channel.send("getting tickets...")
                    await message.channel.send(self.getTickets())
                    fuzzy_time = random.randint(360, 460)
                    time.sleep(fuzzy_time)

        client.run(token)


        self.driver.quit()

if __name__ == "__main__":
    bot = TicketBot()
    bot.main()