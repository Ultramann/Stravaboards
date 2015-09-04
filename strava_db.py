import pandas as pd
from pymongo import MongoClient

def get_big_df():
    client = MongoClient()
    db = client['Strava']
    table = db['Segment_Efforts']
    return pd.DataFrame(list(table.find()))

def make_id_cols(df):
    columns = ['athlete', 'segment']
    for column in columns:
        df['{}_id'.format(column)] = df[column].apply(lambda x: x['id'])

def get_segment_info(df):
    categories = ['average_grade', 'distance', 'elevation_low', 'elevation_high', 'maximum_grade']
    for category in categories:
        df['seg_{}'.format(category)] = df.segment.apply(lambda x: x[category])

def make_date_col(df):
    df['date'] = pd.to_datetime(df.start_date_local)

def engineer_features(df):
    df['tracks_cadence'] = ~pd.isnull(df.average_cadence)
    df['tracks_heartrate'] = ~pd.isnull(df.average_heartrate)

def remove_useless_columns(df):
    columns = ['max_heartrate', 'resource_state', 'name', 'kom_rank', 'start_index', 'pr_rank',
               'id', '_id', 'achievements', 'end_index', 'segment', 'athlete', 'start_date', 
               'start_date_local', 'average_cadence', 'average_heartrate', 'activity']
    df.drop(columns, inplace=True, axis=1)

def get_clean_df():
    df = get_big_df()
    make_id_cols(df)
    get_segment_info(df)
    make_date_col(df)
    engineer_features(df)
    remove_useless_columns(df)
    return df
