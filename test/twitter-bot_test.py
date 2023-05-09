from bots import twitter_bot as tb

class TwitterBotTest:
    def main(self):
        self.bot = tb()

        self.testDateValidator()
    
    def testDateValidator(self):
        # Test 1
        assert self.bot.decidePurchase("2021-10-10") == True


if __name__ == "__main__":
    TwitterBotTest.main()