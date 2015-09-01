import json
from selenium import webdriver

with open('./strava.json') as f:
    data = json.loads(f.read())
    email, password = data["EMAIL"], data["PASSWORD"]

def get_driver(url_extension):
    strava_segment_search_url = 'https://www.strava.com/' + url_extension
    driver = webdriver.PhantomJS()
    driver.get(strava_segment_search_url)
    return driver

def enter_email(driver):
    email_box = driver.find_element_by_name('email')
    email_box.click()
    email_box.send_keys(email)

def enter_password(driver):
    password_box = driver.find_element_by_name('password')
    password_box.click()
    password_box.send_keys(password)

def get_logged_in_driver(url_extension=''):
    driver = get_driver(url_extension)
    enter_email(driver)
    enter_password(driver)
    driver.find_element_by_id('login-button').click()
    return driver
