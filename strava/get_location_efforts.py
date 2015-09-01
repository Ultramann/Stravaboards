import re
import os
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient
from strava_driver import get_logged_in_driver

with open('./strava.json') as f:
    data = json.loads(f.read())
    email, password = data["EMAIL"], data["PASSWORD"]

access_token = '221492179ffd21cc31da6928b13b6ab647c83fc1'
extra_headers = {'Authorization' : 'Bearer %s' % access_token}

url_base = 'https://www.strava.com/api/v3/'
page_max = 200

def enter_search(driver, location):
    search_bar = driver.find_element_by_id('keywords')
    search_bar.click()
    search_bar.send_keys(location)
    driver.find_element_by_id('climb-search-button').click()

def filter_segments(soup):
    refs = [a.attrs['href'] for a in soup.find_all('a', href=True) if 'segments' in a.attrs['href']]
    segments = [re.findall(r'segments/(\d+)', ref) for ref in refs]
    return [int(seg[0]) for seg in segments if len(seg)]

def get_segments(location):
    driver = get_logged_in_driver('/segments/search')
    enter_search(driver, location)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    os.remove('ghostdriver.log')
    return filter_segments(soup)

def get_segment_efforts(segment, num_efforts=None):
    seg_eff_cnt = requests.get(url_base + 'segments/{}'.format(segment), 
                               headers=extra_headers).json()['effort_count'] if not num_efforts \
                                                                               else num_efforts

    return [effort for page in xrange(1, seg_eff_cnt/page_max + 2) 
                for effort in requests.get(url_base + 'segments/{}/all_efforts'.format(segment), 
                                           headers=extra_headers, 
                                           params={'per_page': page_max, 'page': page}).json()]

if __name__ == '__main__':
    client = MongoClient()
    db = client['Strava']
    table = db['Bozeman_efforts']
    segments = get_segments('bozeman, montana')

    for segment in segments:
        for effort in get_segment_efforts(segment):
            if not table.find_one({'activity.id': effort['activity']['id']}):
                table.insert_one(effort)

