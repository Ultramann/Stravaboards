import time
import json
import requests
from sys import stdout
from pymongo import MongoClient

with open('./.strava.json') as f:
    data = json.loads(f.read())
    access_token = data["TOKEN"]
header =  {'Authorization' : 'Bearer %s' % access_token}

url_base = 'https://www.strava.com/api/v3/'
page_max = 200

client = MongoClient()
db = client['Strava']
table = db['segment_efforts']

def update_effort_acquisition(segment_effort_count, page):
    percent_complete = float(page) / (segment_effort_count/page_max + 2) * 100
    stdout.flush()
    stdout.write('   Retrieving {} efforts: {:.1f}% complete \r'.format(segment_effort_count,
                                                                        percent_complete))

def get_page_efforts(page, segment, segment_effort_count):
    page_efforts = requests.get(url_base + 'segments/{}/all_efforts'.format(segment), 
                                headers=header, 
                                params={'per_page': page_max, 'page': page}).json()
    update_effort_acquisition(segment_effort_count, page)
    time.sleep(.5)
    return page_efforts

def get_segment_efforts(segment):
    segment_effort_count = requests.get(url_base + 'segments/{}'.format(segment), 
                                        headers=header).json()['effort_count']
    update_effort_acquisition(segment_effort_count, 0)
    necessary_calls = range(1, segment_effort_count/page_max + 2)
    return [effort for page in necessary_calls 
            for effort in get_page_efforts(page, segment, segment_effort_count) 
                                                    if isinstance(effort, dict)]

def insert_efforts(efforts):
    table.insert_many(efforts)

def get_insert_segment_efforts(segment):
    t1 = time.time()
    efforts = get_segment_efforts(segment)
    stdout.flush()
    stdout.write('   Retrieved {} efforts in {:.2f} minutes'.format(len(efforts), 
                                                                   (time.time() - t1)/60))
    t2 = time.time()
    insert_efforts(efforts)
    print '   Inserted them into database in {:.2f} seconds'.format(time.time() - t2)
    return len(efforts)

if __name__ == '__main__':
    segments = {125, 5642079, 5857327, 4793848, 6048743, 118, 3305098, 356635, 4173351, 4062646, 
                640981, 6135256, 1173191, 4783121, 1723, 6366843, 8429549, 7481858, 651728, 1521, 
                4259807, 6875972, 5611730, 2707292, 7883627, 622149, 2451142, 5836703, 2858097,
                634332, 1077, 8411114, 881888, 3545515, 5099924, 3066267, 3066267, 934409, 633435,
                1003240, 866902, 835833, 8042617, 8727433, 4599878, 6325954, 1759580, 1105154, 
                806005, 1451654, 7531032, 4779241, 2435434, 841251, 2958707, 9008146, 2188435, 
                2627, 6838822, 5079282, 8594904, 7615757, 7615757, 2350753, 2687319, 2350791, 
                2339624, 2687221, 8727940, 844654, 1213534, 5831003, 5134503, 8050750, 798887, 
                7074191, 975395, 612159, 7969432, 1745022, 5292307, 180, 6768781, 5292307, 
                4178476, 925819, 925819, 6173812, 6458467, 4367683, 821934, 866323, 8800675, 
                666315, 2665113, 7186902, 6546684, 2234914, 747045, 8239228, 905184, 3200333, 
                1329495, 814196, 991174, 852755, 8692386, 8285294, 3559004, 6478150, 1042514,
                774591, 351211}
    
    total_efforts = 0
    t_init = time.time()
    for i, segment in enumerate(segments, 1):
        print '{}} Starting segment {}'.format(i, segment)
        total_efforts += get_insert_segment_efforts(segment)
    t_mins = (time.time() - t_init)/60
    print 'Retrieved and inserted {} efforts in {:.2f} minutes'.format(total_efforts, t_mins)

