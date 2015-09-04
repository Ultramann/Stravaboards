import pandas as pd
from strava_db import get_clean_df

def print_num_atheletes_with_efforts_gt(df, nums):
    for num in nums:
        num_aths = len(df.groupby('athlete_id').count().query('activity >= {}'.format(num)))
        print 'Number of athletes with greater than {} efforts in the database: {}'.format(
                                                                                num, num_aths)

if __name__ == '__main__':
    df = get_clean_df()
