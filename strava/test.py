import requests
import time

access_token = '221492179ffd21cc31da6928b13b6ab647c83fc1'
extra_headers = {'Authorization' : 'Bearer %s' % access_token}

url_base = 'https://www.strava.com/api/v3/'
page_max = 200

high_segment = 4783121 # 173,751 attempts by 16,367 people
segment = 5432971 # 6,276 attempts by 1,322 people
segment_effort_count = requests.get(url_base + 'segments/{}'.format(segment), 
                                    headers=extra_headers).json()['effort_count']
t1 = time.time()
all_efforts = reduce(lambda x, y: x + y,
                     map(lambda x: requests.get(url_base + 'segments/{}/all_efforts'.format(segment),
                                                headers=extra_headers, 
                                                params={'per_page': page_max, 'page': x}).json(),
                         range(1, segment_effort_count/page_max + 2)))
print 'Total time for functional: {} seconds'.format(time.time() - t1)

all_efforts_list = []
t2 = time.time()
for page in xrange(1, segment_effort_count/page_max + 2):
    r = requests.get(url_base + 'segments/{}/all_efforts'.format(segment), 
                     headers=extra_headers,
                     params={'per_page': page_max, 'page': page})
    if len(r.json()) != 200: thing = r.json()
    all_efforts_list.extend(r.json())
print 'Total time for list: {} seconds'.format(time.time() - t2)

    #Total time for functional: 27.9667088985 seconds
    #Total time for list: 29.4919791222 seconds

    #Total time for functional: 27.2326579094 seconds
    #Total time for list: 28.2634260654 seconds

    #Total time for functional: 28.1461081505 seconds
    #Total time for list: 29.2313649654 seconds

    #Total time for functional: 29.575619936 seconds
    #Total time for list: 26.975946188 seconds

    #Total time for functional: 30.3280858994 seconds
    #Total time for list: 31.9240109921 seconds

    #Total time for functional: 38.1175589561 seconds
    #Total time for list: 37.7011890411 seconds

    #Total time for functional: 37.4148068428 seconds
    #Total time for list: 38.136040926 seconds
