import sys
sys.path.append('../eda')
from strava_db import EffortDfGetter
import graphlab as gl
import pandas as pd
import numpy as np

def get_df():
    df_getter = EffortDfGetter(origin='json')
    return df_getter.get()

def get_agg_df(df):
    bad_columns_to_keep = ['segment_id', 'athlete_id', 'average_watts', 'distance', 'elapsed_time', 
                       'moving_time', 'tracks_cadence', 'tracks_heartrate', 'average_speed']
    columns_to_keep = ['segment_id', 'athlete_id', 'average_speed']
    columns_to_normalize = ['tracks_heartrate', 'tracks_cadence', 'moving_time']
    agg_df = df.groupby(['segment_id', 'athlete_id']).mean().reset_index()
    agg_df[columns_to_normalize] = (agg_df[columns_to_normalize] - 
                                    agg_df[columns_to_normalize].mean()) / \
                                    agg_df[columns_to_normalize].std()
    return agg_df[columns_to_keep]

def make_cleaner_dfs(dfs, num_features):
    return [pd.concat([df] + [pd.Series(df.factors.apply(lambda x: x[i]), 
                              name='rating_{}'.format(i+1)) for i in range(num_features)],
                      axis=1)  for df in dfs]

def drop_useless_columns(dfs):
    for df in dfs:
        df.drop(['factors'], axis=1, inplace=True)

def get_clean_dfs_from_model(model, num_features):
    model_coefficients = model['coefficients']
    athlete_df = model_coefficients['athlete_id'].to_dataframe()
    segment_df = model_coefficients['segment_id'].to_dataframe()
    cleaner_athlete_df, cleaner_segment_df = make_cleaner_dfs([athlete_df, segment_df], num_features)
    drop_useless_columns([cleaner_athlete_df, cleaner_segment_df])
    cleaner_athlete_df.set_index(['athlete_id'], inplace=True)
    cleaner_segment_df.set_index(['segment_id'], inplace=True)
    return cleaner_athlete_df, cleaner_segment_df

def get_latent_features(sf):
    number_latent_features = 2
    model = gl.factorization_recommender.create(sf, user_id='athlete_id', item_id='segment_id', 
                                                target='average_speed', nmf=True,
                                                regularization=0, linear_regularization=0,
                                                num_factors=number_latent_features)
    athlete_ratings, segment_ratings = get_clean_dfs_from_model(model, number_latent_features)
    return athlete_ratings, segment_ratings

def df_to_latent_features(df):
    agg_df = get_agg_df(df)
    sf = gl.SFrame(agg_df).dropna()
    return get_latent_features(sf)

if __name__ == '__main__':
    df = get_df()
    athlete_ratings, segment_ratings = df_to_latent_features(df)
