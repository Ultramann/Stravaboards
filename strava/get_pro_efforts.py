from bs4 import BeautifulSoup
from strava_driver import get_logged_in_driver

def get_pro_links_list(driver):
    driver.find_element_by_partial_link_text('Pros on Strava').click()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tags = soup.select('a.minimal')
    pro_links = [tag.attrs['href'] for tag in tags]
    return pro_links

if __name__ == '__main__':
    driver = get_logged_in_driver('login')
    pro_links = get_pro_links_list(driver)
