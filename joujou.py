from selenium import webdriver
import geckodriver_autoinstaller


geckodriver_autoinstaller.install()

driver = webdriver.Firefox()