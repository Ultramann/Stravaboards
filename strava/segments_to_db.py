import time
import json
import requests
from pymongo import MongoClient
from multiprocessing import Pool

with open('./.strava.json') as f:
    data = json.loads(f.read())
    access_token = data["TOKEN"]
header =  {'Authorization' : 'Bearer %s' % access_token}

url_base = 'https://www.strava.com/api/v3/'
page_max = 200

client = MongoClient()
db = client['Strava']
table = db['Segment_Efforts']

def get_page_efforts(page):
    return requests.get(url_base + 'segments/{}/all_efforts'.format(segment), 
                        headers=header, 
                        params={'per_page': page_max, 'page': page}).json()

def get_segment_efforts(segment):
    seg_eff_cnt = requests.get(url_base + 'segments/{}'.format(segment), 
                               headers=header).json()['effort_count']

    pool = Pool(processes=3)
    all_efforts = pool.map(get_page_efforts, range(1, seg_eff_cnt/page_max + 2))
    return [effort for effort_list in all_efforts for effort in effort_list]

def insert_effort(effort):
    if (isinstance(effort, dict) and isinstance(effort['activity'], dict)):
        if not table.find_one({'activity.id': effort['activity']['id']}):
            table.insert_one(effort)

def get_insert_segment_efforts(segment):
    t1 = time.time()
    efforts = get_segment_efforts(segment)
    print '   Retrieved {} efforts in {:.2f} minutes'.format(len(efforts), (time.time() - t1)/60)
    t2 = time.time()
    pool = Pool(processes=3)
    pool.map(insert_effort, efforts)
    print '   Inserting them into database in {:.2f} minutes'.format((time.time() - t2)/60)
    return len(efforts)

if __name__ == '__main__':
    segments = [3490822, 5264177, 
                626742, 8643847, 1154584, 3664904, 7330795, 809335, 857898, 954038, 600237, 1262370,
                1549153, 954038, 618199, 1741438, 719341, 638232, 949453, 997901, 3883126, 7197693]
    finished_segments = [6366843, 617239, 904763, 1173191, 1723, 611363, 563888]
    
    total_efforts = 0
    t_init = time.time()
    for i, segment in enumerate(segments):
        print 'Starting segment {}...'.format(i)
        total_efforts += get_insert_segment_efforts(segment)
    t_mins = (time.time() - t_init)/60
    print 'Retrieved and inserted {} efforts in {:.2f} minutes'.format(total_efforts, t_mins)

