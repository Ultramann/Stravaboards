import json
import numpy as np
import pandas as pd
from pymongo import MongoClient

class EffortDfGetter(object):
    '''
    Class for retrieving a DataFrame with Strava efforts from either raw json file or mongo database
    '''
    def __init__(self, origin='json'):
        '''
        Input: String specifiying where the original data is coming from
        '''
        self.origin = origin

    def get(self, size=False):
        '''
        Input: Size if origin is mongo
        Output: Clean DataFrame of Strava efforts
        '''
        self.df = self.get_df_from_json() if self.origin == 'json' else self.get_df_from_mongo(size)
        self.transform_df()
        return self.df

    def transform_df(self):
        '''
        Helper function that calls all necessary functions to change DataFrame into proper type
        '''
        self.make_id_cols()
        self.get_segment_info()
        self.make_date_col()
        self.engineer_features()
        self.remove_useless_rows()
        self.remove_useless_columns()
        self.remove_outliers()

    def get_df_from_json(self):
        '''
        Function to get data from raw json file
        Output: DataFrame from raw json file
        '''
        with open('../data/efforts.json') as f:
            return pd.DataFrame(json.loads(line) for line in f)

    def get_df_from_mongo(self, size=False):
        '''
        Function to get data from raw json file
        Input: Size of dataframe to be retrieved
        Output: DataFrame from mongo database
        '''
        client = MongoClient()
        db = client['Strava']
        table = db['segment_efforts']
        if size:
            df = pd.DataFrame(list(table.find().limit(size)))
        else:
            df = pd.DataFrame(list(table.find()))
        return df

    def make_id_cols(self):
        '''
        Function to parse ids from nested dictionaries
        '''
        # Specify which column names have desired ids
        columns = ['athlete', 'segment', 'activity']

        # Make a new column in the df from each of the ids
        for column in columns:
            self.df['{}_id'.format(column)] = self.df[column].apply(lambda x: x['id'])

    def get_segment_info(self):
        '''
        Function to get the information stored in the nested dictionary about the segment
        '''
        # Specify which elements of the segment dictionary to keep
        categories = ['average_grade', 'distance', 'elevation_low', 
                      'elevation_high', 'maximum_grade']

        # Make a new column in the df for each of the segment elements
        for category in categories:
            self.df['seg_{}'.format(category)] = self.df.segment.apply(lambda x: x[category])

    def make_date_col(self):
        '''
        Function to make datetime column out of date column
        '''
        self.df['date'] = pd.to_datetime(self.df.start_date_local)

    def engineer_features(self):
        '''
        Function to engineer features from now existing columns
        '''
        # Dummies for whether or not the effort had cadence or heartrate tracking for the effort
        self.df['tracks_cadence'] = ~pd.isnull(self.df.average_cadence)
        self.df['tracks_heartrate'] = ~pd.isnull(self.df.average_heartrate)

        # Difference between the specified segment distance and the effort's recorded ride distance
        self.df.eval('dist_diff = seg_distance - distance')

        # Speed = Distance / Time
        self.df.eval('average_speed = distance / elapsed_time')

    def remove_useless_rows(self):
        '''
        Function to get rid of efforts that have no useful information
        '''
        # Only keep efforts with a positive recorded moving time
        self.df = self.df.query('moving_time > 0')

    def remove_useless_columns(self):
        '''
        Function to get rid of columns that are no longer useful
        '''
        # List of useless columns
        columns = ['max_heartrate', 'resource_state', 'name', 'kom_rank', 'start_index', 'pr_rank',
                   'id', '_id', 'achievements', 'end_index', 'segment', 'athlete', 'start_date', 
                   'start_date_local', 'average_cadence', 'average_heartrate', 'activity']
        
        # Drop all the useless columns
        self.df.drop(columns, inplace=True, axis=1)

    def remove_outliers(self):
        '''
        Function to remove athlete effort outliers, as measured by their naively calculated expected
        speed.
        '''
        # Averge speed per athlete
        athlete_average_speed = self.df.groupby('athlete_id', as_index=False).average_speed.mean()

        # Average speed and standard deviation per segment
        segment_average_speed = self.df.groupby('segment_id').average_speed.mean().reset_index()
        segment_speed_std = self.df.groupby('segment_id').average_speed.std().reset_index()

        # Merge all those dfs together
        df = pd.merge(self.df, athlete_average_speed, 
                      on='athlete_id', 
                      how='left', 
                      suffixes=('', '_ath_mean'))

        df = pd.merge(df, segment_average_speed, 
                      on='segment_id', 
                      how='left', 
                      suffixes=('', '_seg_mean'))

        df = pd.merge(df, segment_speed_std, 
                      on='segment_id', 
                      how='left', 
                      suffixes=('', '_seg_std'))

        # Make predicted speed column, average of athlete's average and segment's average
        df.eval('predicted_speed = (average_speed_ath_mean + average_speed_seg_mean) / 2')

        # Inliers equal to only those efforts whoes average_speed are within 4 stds of predicted
        inlier_df = df[np.abs(df.predicted_speed - df.average_speed) < 4 * df.average_speed_seg_std]

        # Set whole df to inliers without added columns
        added_columns = ['average_speed_ath_mean', 'average_speed_seg_mean', 
                         'average_speed_seg_std', 'predicted_speed']
        self.df = inlier_df.drop(added_columns, axis=1)

