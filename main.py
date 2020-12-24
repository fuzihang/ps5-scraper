import os
import selenium
from selenium import webdriver
import time
import io
import requests
from selenium.common.exceptions import ElementClickInterceptedException

from win10toast import ToastNotifier
from datetime import datetime
import multiprocessing as mp
import threading
from email.mime.text import MIMEText

WALMART_URL = 'https://www.walmart.ca/en/video-games/playstation-5/ps5-consoles/N-9857'
AMAZON_URL = 'https://www.amazon.ca/PlayStation-5-Console/dp/B08GSC5D9G'
BESTBUY_DISC_URL = 'https://www.bestbuy.ca/en-ca/product/playstation-5-console-online-only/14962185'
BESTBUY_DIGITAL_URL = 'https://www.bestbuy.ca/en-ca/product/playstation-5-digital-edition-console-online-only/14962184'
EB_GAMES_URL = 'https://www.ebgames.ca/PS5/Games/877522'
TOYSRUS_URL = 'https://www.toysrus.ca/en/PlayStation-5-Digital-Edition/E4A019FE.html'
COSTCO_URL = 'https://www.costco.ca/playstation-5-console-bundle-.product.100696941.html'

# Test urls. Urls below does not container the "out of stock phrases", so could be used to test the behavior when there's stock or when capcha page shows up
test_bb_url = 'https://www.bestbuy.ca/en-ca/product/playstation-5-dualsense-wireless-controller-white/14962193' # this is the DS controller
test_amazon_url = 'https://www.amazon.ca/DualSense-Wireless-Controller/dp/B08GSL374K/ref=sr_1_3?crid=JUT8LMD0U3QS&dchild=1&keywords=ps5+controller&qid=1608779360&s=videogames&sprefix=ps5+c%2Cvideogames%2C174&sr=1-3' # DS controller
test_walmart_url = 'https://www.walmart.ca/en/ip/playstation5-dualsense-wireless-controller/6000202196831' # DS controller
test_eb_url = 'https://www.ebgames.ca/PS5/Games/877512/playstation-5-dualsense-wireless-controller'
test_toysrus_url = 'https://www.toysrus.ca/en/PlayStation-5-DualSense-Wireless-Controller/24DA1B29.html'
test_costco_url = 'https://www.costco.ca/playstation-5-dualsense%e2%84%a2-wireless-controller.product.100701439.html'

# Whether to save screen shots while scraping; could be useful for debug
SAVE_SCREENSHOT = True
SEND_EMAIL = True
from send_email import server, sent_from, to


class tracker:
    def __init__(self, url, driver_location):
        self.url = url
        self.notifier = ToastNotifier()
        self.driver = webdriver.Edge(driver_location)
        self.out_of_stock_key_phrases = []
        self.in_stock_phrases = []
        self.email_interval_seconds = 60
        self.last_email_sent_time = 0
        self.email_msg = MIMEText(f'<a href=\"{self.url}\">{self.url}</a>','html')
        self.email_msg['Subject'] = f'{self.__class__.__name__} sent an alert. go check now'

    def save_screenshot(self):
        os.makedirs(self.__class__.__name__, exist_ok=True)
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
        self.driver.get_screenshot_as_file(f'{self.__class__.__name__}\\{dt_string}.png')

    def track(self):
        try:
            self.driver.get(self.url)
            text = self.driver.find_element_by_tag_name('body').text
        except:
            print('gg in getting result')
            return False

        if SAVE_SCREENSHOT:
            self.save_screenshot()
            # self.driver.quit()
            

        # In stock phrases take higher priority than out of stock phrases
        if any(phrase.lower() in text.lower() for phrase in self.in_stock_phrases):
            print('in stock phrases exist')
            return True
        return not any(phrase.lower() in text.lower() for phrase in self.out_of_stock_key_phrases)
    def alert(self, msg='艹艹艹快去抢ps5啊手慢无！！！！！！'):
        try:
            self.notifier.show_toast(title=self.__class__.__name__, msg=msg, duration=1, threaded=False)
        except:
            print('gg')
        if SEND_EMAIL and int(time.time()) - self.last_email_sent_time > self.email_interval_seconds:
            try:
                server.sendmail(from_addr=sent_from, to_addrs=to, msg=self.email_msg.as_string())
                self.last_email_sent_time = int(time.time())
            except:
                print('gg2')
    def run(self, time_between_try=1):
        while True:
            if self.track():
                self.alert()
            time.sleep(time_between_try)



class Walmart_tracker(tracker):
    def __init__(self, url, driver_location):
        super(Walmart_tracker, self).__init__(url, driver_location)
        self.out_of_stock_key_phrases.extend(["Sorry! We're",  "out of stock"])

    def alert(self):
        super(Walmart_tracker, self).alert(msg="Walmart某些out of stock 关键词不存在，应该是出现了机器人验证，手动去看看")

class Amazon_tracker(tracker):
    def __init__(self, url, driver_location):
        super(Amazon_tracker, self).__init__(url, driver_location)
        self.out_of_stock_key_phrases.append("We don't know when or if this item will be back in stock.")

class Bestbuy_tracker(tracker):
    def __init__(self, url, driver_location):
        super(Bestbuy_tracker, self).__init__(url, driver_location)
        self.out_of_stock_key_phrases.extend(["Coming soon"])
        self.in_stock_phrases.extend(['Available to ship', 'Available for free store pickup', 'Available for Backorder'])

class EB_tracker(tracker):
    def __init__(self, url, driver_location):
        super(EB_tracker, self).__init__(url, driver_location)
        self.out_of_stock_key_phrases.append('OUT OF STOCK')

class ToysRUS_tracker(tracker):
    def __init__(self, url, driver_location):
        super(ToysRUS_tracker, self).__init__(url, driver_location)
        self.out_of_stock_key_phrases.append('out of stock')
        # self.in_stock_phrases.append('in stock')

class Costco_tracker(tracker):
    def __init__(self, url, driver_location):
        super(Costco_tracker, self).__init__(url, driver_location)
        self.out_of_stock_key_phrases.append('out of stock')

    # override here, as costco page contains reviews, need better rules
    def track(self):
        self.driver.get(self.url)
        if self.driver.find_elements_by_id('add-to-cart-btn')[0].get_property('value') == 'Out of Stock':
            return False
        return True

from shutil import copyfile

if __name__ == '__main__':
    # walmart_tracker = Walmart_tracker(test_walmart_url)
    # walmart_tracker.run()

    # amazon_tracker = Amazon_tracker(test_amazon_url)
    # amazon_tracker.run()
    # bb_tracker = Bestbuy_tracker(test_bb_url)
    # bb_tracker.run()

    # eb_tracker = EB_tracker(test_eb_url)
    # eb_tracker.run()

    # toys_tracker = ToysRUS_tracker(TOYSRUS_URL)
    # toys_tracker.run()

    # costco_tracker = Costco_tracker(test_costco_url)
    # costco_tracker.run()

    tracker_classess = [Walmart_tracker, EB_tracker, Bestbuy_tracker, Amazon_tracker, ToysRUS_tracker, Costco_tracker]
    tracker_urls = [WALMART_URL, EB_GAMES_URL, BESTBUY_DISC_URL, AMAZON_URL, TOYSRUS_URL, COSTCO_URL]
    # tracker_urls = [test_walmart_url, test_eb_url, test_bb_url, test_amazon_url, test_toysrus_url, test_costco_url]

    edge_original_driver_loc = 'venv/msedgedriver.exe'
    for i, (tracker_class, url) in enumerate(zip(tracker_classess, tracker_urls)):

        driver_loc = f'venv/msedgedriver_copy_{i}.exe'

        if not os.path.exists(driver_loc):
            copyfile(edge_original_driver_loc, driver_loc)
        tracker = tracker_class(url, driver_loc)
        tracker = threading.Thread(target=tracker.run)
        tracker.start()
        time.sleep(2)

    # walmart_tracker = Walmart_tracker(test_walmart_url)
    # amazon_tracker = Amazon_tracker(test_amazon_url)
    # bestbuy_tracker = Bestbuy_tracker(test_bb_url)
    # eb_tracker = EB_tracker(EB_GAMES_URL)
    # costco_tracker = Costco_tracker(COSTCO_URL)

    # walmart_tracker = threading.Thread(target=walmart_tracker.run)
    # amazon_tracker = threading.Thread(target=amazon_tracker.run)
    # bestbuy_tracker = threading.Thread(target=bestbuy_tracker.run)
    # eb_tracker = threading.Thread(target=eb_tracker.run)
    # costco_tracker = threading.Thread(target=costco_tracker.run)


    # walmart_tracker.start()
    # amazon_tracker.start()
    # bestbuy_tracker.start()

    # eb_tracker.start()
    # costco_tracker.start()

    # amazon_tracker.join()



