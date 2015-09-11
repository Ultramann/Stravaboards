import random
import pandas as pd

def split_efforts(df, date='2015-08-01'):
    '''
    Input:  Full effort DataFrame
    Output: Training effort DF, Testing effort DF

    Chooses subset of efforts filtered by date, so long as the filtered efforts for a single user 
    do not represent all of that users segments or all of a segments efforts.
    '''
    recent_efforts_df = df.query('date > "{}"'.format(date))
    re_counts = pd.Series(recent_efforts_df.groupby(['athlete_id', 'segment_id']).count().date)
    tot_counts = pd.Series(df.groupby(['athlete_id', 'segment_id']).count().date.ix[re_counts.index])

    athlete_segment_pairs = re_counts[~(re_counts == tot_counts)].index
    drop_mask = [index for athlete, segment in athlete_segment_pairs
                       for index in recent_efforts_df.query('athlete_id == {} & segment_id == {}'\
                                             .format(athlete, segment)).index.values]

    testing_df = df.ix[drop_mask]
    training_df = df.drop(drop_mask)

    return training_df, testing_df

