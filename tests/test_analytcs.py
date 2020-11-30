import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

from WebDriverSingleton import WebDriver


class TestAnalyticsGraphic():

  def testIniciateWebDriver(self):
    assert WebDriver().driver is not None

  def testCheckTitle(self):
    title = WebDriver().driver.find_element(By.XPATH, "\
      //div[@class='card-header']/div/span[contains\
        (text(),'Engajamento vs Aquisição')]")
    assert title.is_displayed()

  def testCheckDropdownsource(self):
    drop_down = WebDriver().driver.find_element_by_id(
        'analytics_campaign_source')
    assert drop_down.is_displayed()
    select = WebDriver().driver.find_element_by_class_name(
        'Select-input')
    assert select.is_displayed()

  def testCheckDropdownMidia(self):
    drop_down = WebDriver().driver.find_element_by_id(
        'analytics_campaign_medium')
    assert drop_down.is_displayed()
    select = WebDriver().driver.find_element_by_class_name(
        'Select-input')
    assert select.is_displayed()

  def testCheckDropdownCampainName(self):
    drop_down = WebDriver().driver.find_element_by_id(
        'analytics_campaign_name')
    assert drop_down.is_displayed()
    select = WebDriver().driver.find_element_by_class_name(
        'Select-input')
    assert select.is_displayed()

  def testAnalyzedPages(self):
    pages = WebDriver().driver.find_element(By.XPATH, "\
      //div/span[contains(text(),' /testeopiniao/, /opiniao/')]")
    assert pages.is_displayed()

  def testCheckExportData(self):
    exporting = WebDriver().driver.find_element_by_id(
        'exporting_analytics')
    assert exporting.is_displayed()
    ActionChains(WebDriver().driver).click(exporting).perform()
    export = WebDriver().driver.find_element_by_id(
        'export_analytics_data')
    assert export.is_displayed()
    #ActionChains(WebDriver().driver).click(export).perform()
