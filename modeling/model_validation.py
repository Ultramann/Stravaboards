import random

def split_validation_efforts(df):
    '''
    Input:  Full effort DataFrame
    Output: Training effort DF, Testing effort DF

    Chooses subset of efforts filtered by users who have more than one effort on a segment.
    '''
    training_df = df.copy(deep=True)
    high_effort_count_df = df.groupby(['athlete_id', 'segment_id']).count()
    athlete_segment_pairs = random.sample(high_effort_count_df.query('date > 50').index, 50)
