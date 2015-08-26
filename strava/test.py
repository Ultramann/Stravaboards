import requests

access_token = '221492179ffd21cc31da6928b13b6ab647c83fc1'
extra_headers = {'Authorization' : 'Bearer %s' % access_token}

url_base = 'https://www.strava.com/api/v3/'
r1 = requests.get(url_base + 'activities/321934', headers=extra_headers)
#r2 = requests.get(url_base + 'athletes/{}/stats'.format(r.json()['athlete']['id']), 
#                 headers=extra_headers)
