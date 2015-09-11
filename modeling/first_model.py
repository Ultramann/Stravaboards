import sys
sys.path.append('../eda')
from strava_db import EffortDfGetter
import model_validation as mv
import graphlab as gl
import pandas as pd
import numpy as np
import random

def get_df():
    df_getter = EffortDfGetter(origin='json')
    return df_getter.get()

def get_agg_sf(df):
    columns_to_keep = ['segment_id', 'athlete_id', 'average_speed']#, 'tracks_heartrate', 
                       #'tracks_cadence', 'moving_time', 'elapsed_time', 'distance']
    agg_df = df.groupby(['segment_id', 'athlete_id']).mean().reset_index()
    return gl.SFrame(agg_df[columns_to_keep])

def get_seg_sf(df):
    segment_columns = ['segment_id', 'seg_average_grade', 'seg_distance', 'seg_maximum_grade']
    segment_df = df[segment_columns].groupby('segment_id').first()
    return gl.SFrame(segment_df.reset_index())

def make_cleaner_dfs(dfs, num_features):
    return [pd.concat([df] + [pd.Series(df.factors.apply(lambda x: x[i]), 
                              name='rating_{}'.format(i+1)) for i in range(num_features)],
                      axis=1)  for df in dfs]

def drop_useless_columns(dfs):
    for df in dfs:
        df.drop(['factors', 'linear_terms'], axis=1, inplace=True)

def get_clean_dfs_from_model(model, num_features):
    model_coefficients = model['coefficients']
    athlete_df = model_coefficients['athlete_id'].to_dataframe()
    segment_df = model_coefficients['segment_id'].to_dataframe()
    cleaner_athlete_df, cleaner_segment_df = make_cleaner_dfs([athlete_df, segment_df], num_features)
    drop_useless_columns([cleaner_athlete_df, cleaner_segment_df])
    cleaner_athlete_df.set_index(['athlete_id'], inplace=True)
    cleaner_segment_df.set_index(['segment_id'], inplace=True)
    return cleaner_athlete_df, cleaner_segment_df

def get_latent_features(agg_sf, number_latent_features):
    model = gl.factorization_recommender.create(agg_sf, user_id='athlete_id', item_id='segment_id', 
                                                target='average_speed', 
                                                #item_data=seg_sf,
                                                #side_data_factorization=False,
                                                regularization=0,
                                                linear_regularization=0,
                                                #nmf=True, 
                                                solver='sgd',
                                                max_iterations=100,
                                                num_factors=number_latent_features)
    athlete_ratings, segment_ratings = get_clean_dfs_from_model(model, number_latent_features)
    return athlete_ratings, segment_ratings, model

def df_to_latent_features(df, number_latent_features):
    agg_sf = get_agg_sf(df)
    #seg_sf = get_seg_sf(df)
    return get_latent_features(agg_sf, number_latent_features)

def plot_ratings(ratings_df):
    # Get scale for binning in hist depending on what df we're plotting for
    bins_scale = 5 if ratings_df.index.name == 'segment_id' else 300
    # Plot hist with scaled number of bins
    ratings_df.hist(bins=ratings_df.shape[0]/bins_scale, figsize=(10, 5))
    # Plot random sample of ratings
    sample_ratings = ratings_df.ix[random.sample(ratings_df.index, 50)]
    sample_ratings.plot(kind='bar', stacked='True', figsize=(20, 10))

def evaluate_latent_feature_correlations(df, segment_ratings):
    rating_columns = list(segment_ratings.columns.values) 
    segment_columns = ['seg_average_grade', 'seg_distance', 'seg_maximum_grade'] + rating_columns
                       
    print df.groupby('segment_id').first().merge(segment_ratings, right_index=True, 
                                   left_index=True)[segment_columns].corr()[rating_columns]

if __name__ == '__main__':
    df = get_df()
    training_df, testing_df = mv.split_efforts(df)
    athlete_ratings, segment_ratings, model = df_to_latent_features(training_df, 2)
