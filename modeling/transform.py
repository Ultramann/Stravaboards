import sys
sys.path.append('../eda')
from strava_db import EffortDfGetter
import pandas as pd

def get_df():
    df_getter = EffortDfGetter(origin='json')
    return df_getter.get()

if __name__ == '__main__':
    df = get_df()
