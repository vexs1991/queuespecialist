from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from os import getenv
from random import randint, uniform
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
import logging
from logging import warning, info, debug, error, INFO
import yaml
import sys
import subprocess
import requests

logging.basicConfig(level=INFO, format='%(name)s - %(levelname)s - %(message)s', stream=sys.stdout)
logging.getLogger().addHandler(logging.FileHandler(filename='queue.log'))

first_run = False
login_tries = 0

with open('/headless/queue/config.yaml') as f:
    data = yaml.load(f)

def rand_sleep():
   sleep(randint(data['min_sleep'],data['max_sleep']))

def rand_sleep_short():
   sleep(uniform(data['min_sleep_short'],data['max_sleep_short']))

bot_token=data['tg-bottoken']
chat_id=data['tg-chatid']
username=getenv('TML_USER')
password=getenv('TML_PASS')

vnchost=getenv('MY_HOST')
vncip=getenv('MY_IP')
vncport=getenv('MY_PORT')

chromeOptions = Options()
chromeOptions.add_argument('--no-sandbox')
chromeOptions.add_argument('--disable-dev-shm-usage')
chromeOptions.add_argument('--test-type')
chromeOptions.add_argument('--start-maximized')
chromeOptions.add_argument('--disable-gpu')
chromeOptions.add_argument('--window-size=1920,1080')
chromeOptions.add_argument('--window-position=0,0')
driver = webdriver.Chrome(chrome_options=chromeOptions)

def send_image(image_file):
    apiURL = f'https://api.telegram.org/bot{bot_token}/sendPhoto'

    try:
        response = requests.post(apiURL, json={'chat_id': chat_id, 'photo': image_file})
        print(response.text)
    except Exception as e:
        print(e)


def send_message(msg):
    apiURL = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    try:
        response = requests.post(apiURL, json={'chat_id': chat_id, 'text': msg})
        print(response.text)
    except Exception as e:
        print(e)


def login():
    global login_tries
    #open login page
    driver.get(data['login_url'])
    rand_sleep()

    driver.find_element(By.XPATH, data['sel']['login']['username']).send_keys(username)
    driver.find_element(By.XPATH, data['sel']['login']['password']).send_keys(password)
    rand_sleep()
    driver.find_element(By.XPATH, data['sel']['login']['login_btn']).click()
    login_tries += 1

    if login_tries >= 2:
        error("login did not succeed, waiting for manual interaction; please press [ENTER] to continue")
        input("Press [ENTER] to continue...")
        send_message(f'{vnchost}: http://{vncip}:{vncport}  - login error, please login manually as {username}')
        login_tries = 0

def check_queue_button():
    global first_run
    try:
        queue = WebDriverWait(driver, data['wd']['wait'], poll_frequency=data['wd']['poolint']).until(EC.visibility_of_element_located(
          (By.XPATH, data['sel']['queuebtn'][data['sale']])))
        if not first_run:
            send_message(f'{vnchost}: http://{vncip}:{vncport}  - successfull login as {username}')
            first_run = True
        #driver.find_element(By.XPATH, data['sel']['queuebtn']['presale'])
        info(f'We found the queue button, is it enabled?')
    except TimeoutException:
        warning(f'Could not find queue button')
        send_message(f'{vnchost}: http://{vncip}:{vncport}  - error, queue button not found login as {username}')
        if not driver.current_url == data['findqueue_url']:
            warning(f'we are not on the home site')
            driver.get(data['findqueue_url'])
            if driver.current_url == data['login_url']:
                login()
        return False

    # sanity check
    # for "WorldWide Ticket Sale"

    try:
        if not driver.execute_script("return arguments[0].hasAttribute(\"disabled\");", queue):
            info("button is enabled, trying to click on it")
        queue.click()
    except WebDriverException:
        info("Element is not clickable")

    if data['sel']['queuecheck']['text'] in driver.page_source:
        info("we are in queue now!!")
        send_message(f'{vnchost}: http://{vncip}:{vncport}  - we are in queue now {username}')
        return True

    rand_sleep_short()
    driver.get(data['findqueue_url'])
    return False

def verify_out_off_queue():
    if data['sel']['queuecheck']['text'] in driver.page_source:
        info("still in queue")
        return False
    return True

send_message(f'{vnchost}: http://{vncip}:{vncport}  - RAMP UP PHASE')

login()

queue_button_clickable = False
out_off_queue = False

while not queue_button_clickable:
    try:
        queue_button_clickable = check_queue_button()
    except Exception as e:
        error(e)

#are we sure we are in queue now?

while not out_off_queue:
    try:
        out_off_queue = verify_out_off_queue()
    except Exception as e:
        error(e)
    sleep(1)

warning("out of the queue, let's go!!")
send_message(f'{vnchost}: http://{vncip}:{vncport}  - READY TO ORDER {username}')
# now we alert

# xfce4-terminal -e '/bin/bash -c "/usr/bin/python3 /headless/test.py > /headless/log.txt 2>&1"'

sleep(600)
driver.quit()

#xfce4-screenshooter -f -s ~/screen.jpeg