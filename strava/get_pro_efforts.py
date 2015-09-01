import re
import time
from bs4 import BeautifulSoup
from strava_driver import get_logged_in_driver

url_base = 'https://www.strava.com'

def get_pro_links_list(driver):
    driver.get(url_base + '/pros')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tags = soup.select('a0:a.minimal')
    pro_links = [tag.attrs['href'] for tag in tags]
    return pro_links

def get_pro_week_activities(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    a_refs = [a.attrs['href'] for a in soup.find_all('a0:a', href=True) 
                                    if 'activities' in a.attrs['href']]
    activities_list = [re.findall(r'activities/(\d+)', a_ref) for a_ref in a_refs]
    return [int(act[0]) for act in activities_list if len(act)]


def get_pro_activities(driver, pro):
    activities = set()
    driver.get(url_base + pro)
    time.sleep(5)
    for bar in driver.find_elements_by_xpath("//a[contains(@class, 'bar')]"):
        bar.click()
        activities.update(get_pro_week_activities(driver))
    return activities

if __name__ == '__main__':
    driver = get_logged_in_driver('/login', 1)
    pro_links = get_pro_links_list(driver)
    activities = get_pro_activities(driver, pro_links[0])
