import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

from WebDriverSingleton import WebDriver


class TestCommentsGraphic():

  def testIniciateWebDriver(self):
    assert WebDriver().driver is not None

  def testCheckTitle(self):
    title = WebDriver().driver.find_element(By.XPATH, "\
      //div[@class='card-header']/div/span[contains\
        (text(),'Votos e participação em todos os comentários.')]")
    assert title.is_displayed()

 # def testCheckConversationLink(self):
  #  link = WebDriver().driver.find_element_by_link_text(
   #   'https://www.ejplatform.org/login/?next=/conversations/56/ucc-conversa-1/'
    #)
    #assert link.is_displayed()
   # link.click()

  def testCheckInputParticipation(self):
    participation = drop_down = WebDriver().driver.find_element_by_id(
        'participation')
    assert participation.is_displayed()
    participation.send_keys('10' + Keys.ENTER)

  def testCheckDropdownOrdenar(self):
    drop_down = WebDriver().driver.find_element_by_id(
        '_filter')
    assert drop_down.is_displayed()

    select = WebDriver().driver.find_element_by_class_name(
        'Select-input')
    assert select.is_displayed()

  def testCheckExportData(self):
    exporting = WebDriver().driver.find_element_by_id(
        'exporting_comments')
    assert exporting.is_displayed()
    ActionChains(WebDriver().driver).click(exporting).perform()
    export = WebDriver().driver.find_element_by_id(
        'export_comments_data')
    assert export.is_displayed()
    #ActionChains(WebDriver().driver).click(export).perform()
