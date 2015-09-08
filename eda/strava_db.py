import json
import pandas as pd
from pymongo import MongoClient

class EffortDfGetter(object):
    def __init__(self, origin='json'):
        self.origin = origin

    def get(self, size=False):
        self.df = self.get_df_from_json() if self.origin == 'json' else self.get_df_from_mongo(size)
        self.transform_df()
        return self.df

    def transform_df(self):
        self.make_id_cols()
        self.get_segment_info()
        self.make_date_col()
        self.engineer_features()
        self.remove_useless_rows()
        self.remove_useless_columns()

    def get_df_from_json(self):
        with open('../data/efforts.json') as f:
            return pd.DataFrame(json.loads(line) for line in f)

    def get_df_from_mongo(self, size=False):
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
        self.df.eval('dist_diff = seg_distance - distance')

    def remove_useless_rows(self):
        self.df = self.df.query('moving_time > 0')

    def remove_useless_columns(self):
        columns = ['max_heartrate', 'resource_state', 'name', 'kom_rank', 'start_index', 'pr_rank',
                   'id', '_id', 'achievements', 'end_index', 'segment', 'athlete', 'start_date', 
                   'start_date_local', 'average_cadence', 'average_heartrate', 'activity']
        self.df.drop(columns, inplace=True, axis=1)
