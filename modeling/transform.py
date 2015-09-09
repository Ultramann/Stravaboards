import sys
sys.path.append('../eda')
from strava_db import EffortDfGetter
import graphlab as gl
import pandas as pd
import numpy as np

def get_df():
    df_getter = EffortDfGetter(origin='json')
    return df_getter.get()

def get_simple_df(df):
    pivot_df = pd.pivot_table(df, values='average_speed', index='segment_id', 
                          columns=['athlete_id'], aggfunc=np.mean)
    return pivot_df.unstack().reset_index(name='average_speed')

def make_cleaner_dfs(dfs):
    return [pd.concat(df, pd.Series(df.factors.apply(lambda x: x[0]), name='rating')) for df in dfs]

def get_clean_dfs_from_model(model):
    model_coefficients = model['coefficients']
    athlete_df = model_coefficients['athlete_id'].to_dataframe().set_index('athlete_id', 
                                                                            inplace=True)
    segment_df = model_coefficients['segment_id'].to_dataframe().set_index('segment_id',
                                                                            inplace=True)
    cleaner_athlete_df, cleaner_segment_df = *make_cleaner_dfs([athlete_df, segment_df])

def get_latent_features(sf):
    model = gl.factorization_recommender.create(sf, user_id='athlete_id', item_id='segment_id', 
                                                target='average_speed', num_factors=1)
    


if __name__ == '__main__':
    df = get_df()
    simple_df = get_simple_df(df)
    sf = gl.SFrame(simple_df).dropna()
