import pytest
from selenium.webdriver.common.by import By

from WebDriverSingleton import WebDriver


class TestDashboard():

  def testIniciateWebDriver(self):
    assert WebDriver().driver is not None

  opener = WebDriver.dashboard_opener()

  def testTitle(self):
    title = WebDriver().driver.title
    assert title == 'Dash'

  def testCheckEJImg(self):
    img = WebDriver().driver.find_element(By.XPATH, "//img[\
      contains(@src,'./assets/logo-ej-mini.png')]")
    assert img.is_displayed()

  def testCheckButtonReload(self):
    app_reload = WebDriver().driver.find_element(By.ID, 'app_reload')
    assert app_reload.is_displayed()

  def testCheckGraphicsCards(self):
    graphics = len(
        WebDriver().driver.find_elements_by_class_name('card'))
    assert graphics == 3
