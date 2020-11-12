import unittest
import os

import numpy as np
import scipy.interpolate as si
import requests

from datetime import datetime
from time import sleep
from random import uniform

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


# Randomization Related
MIN_RAND = 0.64
MAX_RAND = 1.27
LONG_MIN_RAND = 4.78
LONG_MAX_RAND = 11.1
delayTime = 2
audioToTextDelay = 10


class ZoomBot(unittest.TestCase):

    url1 = None
    url2 = None
    headless = False
    options = None
    profile = None
    capabilities = None
    filename = 'captcha_audio.mp3'
    audioBtnFound = False
    audioBtnIndex = -1

   # Setup options for webdriver
    def setUpOptions(self):
        self.options = webdriver.FirefoxOptions()
        # self.options.add_option('useAutomationExtension', False)
        self.options.headless = self.headless

    # Setup profile
    def setUpProfile(self):
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference(
            "security.fileuri.strict_origin_policy", False)
        self.profile.update_preferences()

    # Enable Marionette, An automation driver for Mozilla's Gecko engine
    def setUpCapabilities(self):
        self.capabilities = webdriver.DesiredCapabilities.FIREFOX
        self.capabilities['marionette'] = True

    # Setup settings
    def setUp(self):
        self.setUpProfile()
        self.setUpOptions()
        self.setUpCapabilities()

        self.driver = webdriver.Firefox(options=self.options, capabilities=self.capabilities,
                                        firefox_profile=self.profile, executable_path='./geckodriver_macOS')

    # Simple logging method
    def log(s, t=None):
        now = datetime.now()
        if t == None:
            t = "Main"
        print(f"{now.strftime('%H:%M:%S')} :: {t} -> {s}")

    # Use time.sleep for waiting and uniform for randomizing
    def wait_between(self, a, b):
        rand = uniform(a, b)
        sleep(rand)

    def audioToText(self, mp3Path, driver):
        driver.execute_script('''window.open("","_blank");''')
        driver.switch_to.window(driver.window_handles[1])

        driver.get('https://speech-to-text-demo.ng.bluemix.net/')

        # Upload file
        sleep(1)
        driver.execute_script("window.scrollTo(0, 1000);")
        btn = driver.find_element(By.XPATH, '//*[@id="root"]/div/input')
        btn.send_keys(mp3Path)

        # Audio to text is processing
        sleep(audioToTextDelay)

        driver.execute_script("window.scrollTo(0, 1000);")
        text = driver.find_elements(
            By.XPATH, '//*[@id="root"]/div/div[6]/div/div/div/span')
        result = " ".join([each.text for each in text])

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        return result

    def saveFile(self, content, filename):
        with open(filename, "wb") as handle:
            for data in content.iter_content():
                handle.write(data)

    # Using B-spline for simulate humane like mouse movments
    def human_like_mouse_move(self, action, start_element):
        points = [[6, 2], [3, 2], [0, 0], [0, 2]]
        points = np.array(points)
        x = points[:, 0]
        y = points[:, 1]

        t = range(len(points))
        ipl_t = np.linspace(0.0, len(points) - 1, 100)

        x_tup = si.splrep(t, x, k=1)
        y_tup = si.splrep(t, y, k=1)

        x_list = list(x_tup)
        xl = x.tolist()
        x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]

        y_list = list(y_tup)
        yl = y.tolist()
        y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]

        x_i = si.splev(ipl_t, x_list)
        y_i = si.splev(ipl_t, y_list)

        startElement = start_element

        action.move_to_element(startElement)
        action.perform()

        c = 5  # change it for more move
        i = 0
        for mouse_x, mouse_y in zip(x_i, y_i):
            action.move_by_offset(mouse_x, mouse_y)
            action.perform()
            self.log(f"Move mouse to, {mouse_x}:{mouse_y}")
            i += 1
            if i == c:
                break

    def do_captcha(self, driver):

        driver.switch_to.default_content()
        self.log("Switch to new frame")
        iframes = driver.find_elements_by_tag_name("iframe")
        driver.switch_to.frame(iframes[0])

        self.log("Wait")
        self.wait_between(LONG_MIN_RAND, LONG_MAX_RAND)

        self.log("Switch Frame")
        for index in range(len(iframes)):
            driver.switch_to.default_content()
            iframe = iframes[index]
            driver.switch_to.frame(iframe)
            driver.implicitly_wait(delayTime)
            try:
                audio_btn = driver.find_element_by_id('recaptcha-audio-button')
                self.log("Mouse movements")
                action = ActionChains(driver)
                self.human_like_mouse_move(action, audio_btn)
                audio_btn.click()
                self.audioBtnFound = True
                self.audioBtnIndex = index
                break
            except Exception as e:
                print(e)

        self.log("Wait")
        self.wait_between(LONG_MIN_RAND, LONG_MAX_RAND)

        if self.audioBtnFound:
            try:
                while True:
                    href = driver.find_element_by_id(
                        'audio-source').get_attribute('src')
                    response = requests.get(href, stream=True)
                    self.saveFile(response, self.filename)
                    response = self.audioToText(
                        f"{os.getcwd()}/{self.filename}", driver)

                    driver.switch_to.default_content
                    iframe = driver.find_elements_by_tag_name(
                        'iframe')[self.audioBtnIndex]
                    driver.switch_to.frame(iframe)

                    inputbtn = driver.find_element_by_id('audio-response')
                    inputbtn.send_keys(response)
                    inputbtn.send_keys(Keys.ENTER)

                    sleep(2)
                    errorMsg = driver.find_elements_by_class_name(
                        'rc-audiochallenge-error-message')[0]

                    if errorMsg.text == "" or errorMsg.value_of_css_property('display') == 'none':
                        print("\n[>] Success")
                        break
            except Exception as e:
                print(e)

        else:
            print('\n[>] Button not found. This should not happen.')

        self.log("Wait")
        driver.implicitly_wait(5)

    # Main function
    def test_run(self):
        driver = self.driver
        driver.set_window_position(0, 0)
        driver.set_window_size(1680, 720)
        url1 = self.url1
        url2 = self.url2

        self.log("Start get1")
        driver.get(url1)
        self.log("End get1")

        self.log("Wait for site to load")
        self.wait_between(MIN_RAND, MAX_RAND)

        email = driver.find_element(By.XPATH, '//*[@id="email"]')
        email.send_keys('davideytanohayon@gmail.com')

        password = driver.find_element(By.XPATH, '//*[@id="password"]')
        password.send_keys('h+rZ5_/Nc=f9_!V')

        self.log("Wait for join btn")
        self.wait_between(LONG_MIN_RAND, LONG_MAX_RAND)

        join_btn = driver.find_element(
            By.XPATH, '//*[@id="login-form"]/div[4]/div/div[1]/button')
        join_btn.click()

        self.log("Wait for recaptcha")
        self.wait_between(LONG_MIN_RAND, LONG_MAX_RAND)

        self.do_captcha(driver)

        self.log("Wait for second site")
        self.wait_between(MIN_RAND, MAX_RAND)

        self.log("Start get2")
        driver.get(url2)
        self.log("End get2")

        self.log("Wait for second site to load")
        self.wait_between(MIN_RAND, MAX_RAND)
        join_btn = driver.find_element_by_xpath('//*[@id="joinBtn"]')
        join_btn.click()

        print('Joined!')
        self.log("Done")

    def tearDown(self):
        self.wait_between(21.13, 31.05)


if __name__ == "__main__":
    # sign in into zoom
    ZoomBot.url1 = 'https://zoom.us/signin'
    # zoom class link
    ZoomBot.url2 = 'https://edu-il.zoom.us/wc/join/2960827055'
    unittest.main()
