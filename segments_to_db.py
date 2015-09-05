import time
import json
import requests
from sys import stdout
from pymongo import MongoClient

class StravaSegmentsGetter(object):
    def __init__(self):
        with open('./.strava.json') as f:
            data = json.loads(f.read())
            access_token = data["TOKEN"]
        client = MongoClient()
        db = client['Strava']
        self.table = db['segment_efforts']
        self.header =  {'Authorization' : 'Bearer %s' % access_token}
        self.url_base = 'https://www.strava.com/api/v3/'
        self.page_max = 200

    def get_segments_efforts(self, segments):
        # Initialize variables for retrieval process
        self.segments = segments
        self.total_efforts = 0
        self.current_segment = None

        # Start retrieval process
        self.time_init = time.time()
        self.get_insert_efforts()
        self.print_final_metrics()

    def get_insert_efforts(self):
        for i, segment in enumerate(self.segments, 1):
            if self.table.find_one({'segment.id': segment}):
                print '{}) Skipped segment {}, already in database'.format(1, segment)
                continue
            print '{}) Starting segment {}'.format(i, segment)
            self.current_segment = segment
            self.get_insert_current_segment_efforts()

    def get_insert_current_segment_efforts(self):
        self.get_time_current_segment_efforts()
        self.insert_time_current_segment_efforts()

    def get_time_current_segment_efforts(self):
        self.time = time.time()
        self.current_efforts = self.get_current_segment_efforts()
        stdout.flush()
        print '   Retrieved {} efforts in {:.2f} minutes '.format(len(self.current_efforts), 
                                                                  (time.time() - t)/60) + ' '*50

    def get_current_segment_efforts(self):
        self.current_segment_effort_count = requests.get(self.url_base + 
                                            'segments/{}'.format(self.current_segment), 
                                            headers=self.header).json()['effort_count']
        self.update_effort_acquisition(0)
        necessary_calls = range(1, self.current_segment_effort_count/self.page_max + 2)
        return [effort for page in necessary_calls 
                for effort in self.get_page_efforts(page)
                if isinstance(effort, dict)]

    def get_page_efforts(self, page):
        page_efforts = requests.get(self.url_base + 
                                    'segments/{}/all_efforts'.format(self.current_segment), 
                                    headers=self.header, 
                                    params={'per_page': self.page_max, 'page': page}).json()
        self.update_effort_acquisition(page)
        time.sleep(.5)
        return page_efforts

    def update_effort_acquisition(self, page):
        percent_complete = float(page) / (self.current_segment_effort_count/self.page_max + 2) * 100
        time_elapsed = time.time() - self.time
        eta = (time_elapsed * 1/(percent_complete/100)) - time_elapsed if page else 10000
        stdout.flush()
        stdout.write('   Retrieving {} efforts: {:.1f}% complete --- Estimated time remaining: {:.1f} seconds                 \r'.format(self.current_segment_effort_count, percent_complete, eta))

    def insert_time_current_segment_efforts(self):
        t = time.time()
        self.table.insert_many(self.current_efforts)
        stdout.flush()
        print '   Inserted them into database in {:.2f} seconds'.format(time.time() - t)
        self.total_efforts += len(self.current_efforts)

    def print_final_metrics(self):
        total_mins = (time.time() - self.time_init)/60
        print 'Retrieved and inserted {} efforts in {:.2f} minutes'.format(self.total_efforts, 
                                                                           total_mins)

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
    
    segment_getter = StravaSegmentsGetter()
    segment_getter.get_segments_efforts(segments)
