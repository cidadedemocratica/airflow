import os.path
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class WebDriver:
    class __WebDriver:
        def __init__(self):
            self.options = Options()
            self.options.add_argument('--disable-extensions')
            self.options.add_argument('--headless')
            self.options.add_argument('--disable-gpu')
            self.options.add_argument('--no-sandbox')
            self.driver = webdriver.Chrome(options=self.options)
            self.driver.implicitly_wait(15)
        
    driver = None

    def __init__(self):
            if not self.driver:
                WebDriver.driver = WebDriver.__WebDriver().driver
       
    def dashboard_opener():
        driver = WebDriver().driver
        driver.get("http://localhost:8050/")

    def teardown_method():
        #while not os.path.exists("votes-ej-raw-data.csv"):
        #    time.sleep(1)
        driver = WebDriver().driver
        driver.quit()
