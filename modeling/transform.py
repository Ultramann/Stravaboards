import sys
sys.path.append('../eda')
from strava_db import EffortDfGetter
import pandas as pd
import numpy as np

def get_df():
    df_getter = EffortDfGetter(origin='json')
    return df_getter.get()

def get_pivot_df(df):
    return pd.pivot_table(df, values='average_speed', index='athlete_id', 
                          columns=['segment_id'], aggfunc=np.mean)

if __name__ == '__main__':
    df = get_df()
    pivot_df = get_pivot_df(df)
