import json
import requests
from selenium import webdriver

access_token = '221492179ffd21cc31da6928b13b6ab647c83fc1'
extra_headers = {'Authorization' : 'Bearer %s' % access_token}

url_base = 'https://www.strava.com/api/v3/'
page_max = 200

with open('./.strava.json') as f:
    data = json.loads(f.read())
    email, password = data["EMAIL"], data["PASSWORD"]

def get_driver(url_extension, browser):
    strava_segment_search_url = 'https://www.strava.com' + url_extension
    driver = webdriver.PhantomJS() if not browser else webdriver.Firefox()
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

def get_logged_in_driver(url_extension='', browser=0):
    driver = get_driver(url_extension, browser)
    enter_email(driver)
    enter_password(driver)
    driver.find_element_by_id('login-button').click()
    return driver

def get_segment_efforts(segment, num_efforts=None):
    seg_eff_cnt = requests.get(url_base + 'segments/{}'.format(segment), 
                               headers=extra_headers).json()['effort_count'] if not num_efforts \
                                                                               else num_efforts
    return [effort for page in xrange(1, seg_eff_cnt/page_max + 2) 
                for effort in requests.get(url_base + 'segments/{}/all_efforts'.format(segment), 
                                           headers=extra_headers, 
                                           params={'per_page': page_max, 'page': page}).json()]
