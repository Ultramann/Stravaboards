import random
import numpy as np
import pandas as pd
import graphlab as gl

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
    # Get list of rating column names
    rating_columns = list(segment_ratings.columns.values) 

    # Make list of all columns to grab from full dataframe
    segment_columns = ['seg_average_grade', 'seg_distance', 'seg_maximum_grade'] + rating_columns
                       
    # Get one instance of all info for each segment
    segment_df = df.groupby('segment_id').first()

    # Join segment info with the latent feature ratings for each segment
    segment_correlation = segment_df.merge(segment_ratings, right_index=True, 
                                           left_index=True)[segment_columns].corr()

    # Return just the rating columns from the correlation df
    return segment_correlation[rating_columns]

def split_efforts(df, date='2015-08-01'):
    '''
    Input:  Full effort DataFrame
    Output: Training effort DF, Testing effort DF

    Chooses subset of efforts filtered by date, so long as the filtered efforts for a single user 
    do not represent all of that users segments or all of a segments efforts.
    '''
    # Get dataframe of all efforts that occurred after "date"
    recent_efforts_df = df.query('date > "{}"'.format(date))

    # Get the segment counts for each athlete after date and in full data set
    recent_seg_count = pd.Series(recent_efforts_df.groupby('athlete_id').count().segment_id)
    tot_seg_count = pd.Series(df.groupby('athlete_id').count().segment_id.ix[recent_seg_count.index])

    # Grab only athletes who ridden on other segments before "date"
    eligible_athletes = recent_seg_count[~(recent_seg_count == tot_seg_count)].index
    test_mask = [index for athlete in eligible_athletes
                       for index in recent_efforts_df.query('athlete_id == {}'.format(athlete)
                                                                             ).index.values]

    # Make training and testing subset dfs of the full df from eligble athlete mask
    testing_df = df.ix[test_mask]
    training_df = df.drop(test_mask)

    return training_df, testing_df

def testing_rmse(model, testing_df):
    '''
    Input: Trained GraphLab recommender model, Test observation DataFrame
    Output: RMSE for testing_df

    Get the root mean squared error for the test data's predicted values from the model
    '''
    # Make appropriate SFrame out of testing data for prediction
    test_sf = gl.SFrame(testing_df[['athlete_id', 'segment_id', 'average_speed']])

    # Predict on testing data SFrame with model
    predictions = np.array(model.predict(test_sf))

    # Calculate root mean squared error between actual test data and predicted values from model
    rmse = (((testing_df.average_speed.values - predictions) ** 2) ** 0.5).sum() / \
                                                                    predictions.shape[0]
    return rmse
