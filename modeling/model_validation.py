import random

def split_efforts(df, count=2000, gt_value=50, total_frac=0.5):
    '''
    Input:  Full effort DataFrame
    Output: Training effort DF, Testing effort DF

    Chooses subset of efforts filtered by users who have more than one effort on a segment.
    '''
    high_effort_count_df = df.groupby(['athlete_id', 'segment_id']).count()
    athlete_segment_pairs = random.sample(high_effort_count_df.query('date > {}'.format(
                                                                    gt_value)).index, count)
    drop_mask = [index for athlete, segment in athlete_segment_pairs
                       for index in random.sample(df.query('athlete_id == {} & segment_id == {}' \
                                                           .format(athlete, segment)).index.values,
                                                  int(gt_value * total_frac))]
    testing_df = df.ix[drop_mask]
    training_df = df.drop(drop_mask)
    return training_df, testing_df

