import re
import os
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient
from strava_lib import get_segment_efforts
from strava_driver import get_logged_in_driver

with open('./.strava.json') as f:
    data = json.loads(f.read())
    email, password = data["EMAIL"], data["PASSWORD"]

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

if __name__ == '__main__':
    client = MongoClient()
    db = client['Strava']
    table = db['Bozeman_efforts']
    segments = get_segments('manhattan, mt')

    for segment in segments:
        for effort in get_segment_efforts(segment):
            if not table.find_one({'activity.id': effort['activity']['id']}):
                table.insert_one(effort)

