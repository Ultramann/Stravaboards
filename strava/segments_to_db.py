import json
import requests
from pymongo import MongoClient
from multiprocessing import Pool

def get_header():
    with open('./.strava.json') as f:
        data = json.loads(f.read())
        access_token = data["TOKEN"]
    return  {'Authorization' : 'Bearer %s' % access_token}

client = MongoClient()
db = client['Strava']
table = db['Segment_Efforts']

def get_segment_efforts(segment):
    header = get_header()
    url_base = 'https://www.strava.com/api/v3/'
    page_max = 200
    seg_eff_cnt = requests.get(url_base + 'segments/{}'.format(segment), 
                               headers=header).json()['effort_count']

    return [effort for page in xrange(1, seg_eff_cnt/page_max + 2) 
                for effort in requests.get(url_base + 'segments/{}/all_efforts'.format(segment), 
                                           headers=header, 
                                           params={'per_page': page_max, 'page': page}).json()]

def insert_effort(effort):
    if (isinstance(effort, dict) and isinstance(effort['activity'], dict)):
        if not table.find_one({'activity.id': effort['activity']['id']}):
            table.insert_one(effort)

def get_insert_segment_efforts(segment):
    efforts = get_segment_efforts(segment)
    print '   Finished collecting efforts'
    pool = Pool(processes=4)
    pool.map(insert_effort, efforts)
    print '   Finished inserting efforts'

if __name__ == '__main__':
    segments = [6366843, 617239, 904763, 1173191, 1723, 611363, 563888, 2386958, 3490822, 5264177, 
                626742, 8643847, 1154584, 3664904, 7330795, 809335, 857898, 954038, 600237, 1262370,
                1549153, 954038, 618199, 1741438, 719341, 638232, 949453, 997901, 3883126, 7197693]
    test_segments = [825868, 298337, 1741438]
    
    for i, segment in enumerate(test_segments):
        print 'Starting segment {}...'.format(i)
        get_insert_segment_efforts(segment)

