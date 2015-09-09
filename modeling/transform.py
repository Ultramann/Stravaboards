import sys
sys.path.append('../eda')
from strava_db import EffortDfGetter
import graphlab as gl
import pandas as pd
import numpy as np

def get_df():
    df_getter = EffortDfGetter(origin='json')
    return df_getter.get()

def get_pivot_df(df):
    return pd.pivot_table(df, values='average_speed', index='athlete_id', 
                          columns=['segment_id'], aggfunc=np.mean)
def get_simple_df(df):
    return df.unstack().reset_index(name='average_speed')

if __name__ == '__main__':
    df = get_df()
    pivot_df = get_pivot_df(df)
    simple_df = get_simple_df(pivot_df)
    sf = gl.SFrame(simple_df).dropna()
