#from pyvirtualdisplay import Display
from xvfbwrapper import Xvfb
import os,time,sys
from selenium import webdriver
sys.path.append(os.path.abspath(os.getcwd()))

class Driver():
    def __init__(self):
        self.driver=None
# Setting up Selenium
    def init(self):
        if self.driver is not None:
            self.delete_driver()
        DRIVER_PATH = "data/chromedriver"
        self.display=Xvfb()
        #self.display=Display(visible=0)
        self.display.start()

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.1 Safari/605.1.15")

        self.driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)

       # self.driver.execute_script("navigator.geolocation.getCurrentPosition = function(success) { success({coords: {latitude: 50.455755, longitude: 30.511565}}); }")

    def delete_driver(self):
        self.display.stop()
        self.driver.quit()