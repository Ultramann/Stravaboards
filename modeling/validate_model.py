import random
import pandas as pd

def plot_ratings(ratings_df):
    '''
    Input: DataFrame of decomposed ratings
    Output: None

    Plots histogram of the ratings in ratings_df and a sample from the frame
    '''
    # Get scale for binning in hist depending on what df we're plotting for
    bins_scale = 5 if ratings_df.index.name == 'segment_id' else 300

    # Plot hist with scaled number of bins
    ratings_df.hist(bins=ratings_df.shape[0]/bins_scale, figsize=(10, 5))

    # Plot random sample of ratings
    sample_ratings = ratings_df.ix[random.sample(ratings_df.index, 50)]
    sample_ratings.plot(kind='bar', stacked='True', figsize=(20, 10))

def evaluate_latent_feature_correlations(df, segment_ratings):
    '''
    Input: Training DataFrame, DataFrame of segment ratings
    Output: Correlation matrix for the ratings from segment_ratings
    '''
    rating_columns = list(segment_ratings.columns.values) 
    segment_columns = ['seg_average_grade', 'seg_distance', 'seg_maximum_grade'] + rating_columns
                       
    return df.groupby('segment_id').first().merge(segment_ratings, right_index=True, 
                                   left_index=True)[segment_columns].corr()[rating_columns]

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

    
