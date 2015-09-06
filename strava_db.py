import time
import json
import requests
import pandas as pd
from sys import stdout
from pymongo import MongoClient

class EffortDfGetter(object):
    def __init__(self, origin='json'):
        self.origin = origin

    def get(self, size=False):
        self.df = pd.read_json('Somthing from S3') if self.origin == 'json' \
                                                   else self.get_big_df_from_mongo(size)
        self.transform_df()
        return self.df

    def transform_df(self):
        self.make_id_cols()
        self.get_segment_info()
        self.make_date_col()
        self.engineer_features()
        self.remove_useless_columns()

    def get_big_df_from_mongo(self, size=False):
        client = MongoClient()
        db = client['Strava']
        table = db['segment_efforts']
        if size:
            df = pd.DataFrame(list(table.find().limit(size)))
        else:
            df = pd.DataFrame(list(table.find()))
        return df

    def make_id_cols(self):
        columns = ['athlete', 'segment', 'activity']
        for column in columns:
            self.df['{}_id'.format(column)] = self.df[column].apply(lambda x: x['id'])

    def get_segment_info(self):
        categories = ['average_grade', 'distance', 'elevation_low', 
                      'elevation_high', 'maximum_grade']
        for category in categories:
            self.df['seg_{}'.format(category)] = self.df.segment.apply(lambda x: x[category])

    def make_date_col(self):
        self.df['date'] = pd.to_datetime(self.df.start_date_local)

    def engineer_features(self):
        self.df['tracks_cadence'] = ~pd.isnull(self.df.average_cadence)
        self.df['tracks_heartrate'] = ~pd.isnull(self.df.average_heartrate)

    def remove_useless_columns(self):
        columns = ['max_heartrate', 'resource_state', 'name', 'kom_rank', 'start_index', 'pr_rank',
                   'id', '_id', 'achievements', 'end_index', 'segment', 'athlete', 'start_date', 
                   'start_date_local', 'average_cadence', 'average_heartrate', 'activity']
        self.df.drop(columns, inplace=True, axis=1)



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
                print '{}) Skipped segment {}, already in database'.format(i, segment)
                continue
            print '{}) Starting segment {}'.format(i, segment)
            self.current_segment = segment
            self.get_insert_current_segment_efforts()

    def get_insert_current_segment_efforts(self):
        self.get_time_current_segment_efforts()
        self.insert_current_segment_efforts()

    def get_time_current_segment_efforts(self):
        self.time = time.time()
        self.current_efforts = self.get_current_segment_efforts()
        stdout.flush()
        print '   Retrieved {} efforts in {:.2f} minutes '.format(len(self.current_efforts), 
                                                            (time.time() - self.time)/60) + ' '*55

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
        time.sleep(1)
        return page_efforts

    def update_effort_acquisition(self, page):
        percent_complete = float(page) / (self.current_segment_effort_count/self.page_max + 2) * 100
        time_elapsed = time.time() - self.time
        eta = (time_elapsed * 1/(percent_complete/100)) - time_elapsed if page else 100000
        stdout.flush()
        stdout.write('   Retrieving {} efforts: {:.1f}% complete --- Estimated time remaining: {:.1f} seconds            \r'.format(self.current_segment_effort_count, percent_complete, eta))

    def insert_current_segment_efforts(self):
        self.table.insert_many(self.current_efforts)
        self.total_efforts += len(self.current_efforts)

    def print_final_metrics(self):
        total_mins = (time.time() - self.time_init)/60
        print 'Retrieved and inserted {} efforts in {:.2f} minutes'.format(self.total_efforts, 
                                                                           total_mins)

