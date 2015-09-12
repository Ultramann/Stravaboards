import numpy as np

def scale_ratings(ratings_df):
    '''
    Input: DataFrame of latent features (ratings)
    Output: Positively ratings on scale from 0 - 100 
    '''
    ratings_df += abs(ratings_df.min())
    ratings_df *= 100. / ratings_df.max() 
    return ratings_df
    
def get_n_leaders(ratings_df, rating_column, n=20):
    '''
    Input: DataFrame of latent features, Column from user latent feature (rating) matrix
    Output: DataFrame of top n leaders and their ratings
    '''
    sorted_ratings_indexes = np.argsort(ratings_df[rating_column].values)
    top_n_indexes = sorted_ratings_indexes[-1:-n-1:-1]
    n_leaders_df = ratings_df.loc[top_n_indexes][rating_column]
    n_leaders_df['rank'] = range(1, n+1)
    return n_leaders_df

def get_all_leader_boards(ratings_df, n_leaders=20):
    '''
    Input: DataFrame of latent features
    Output: List of DataFrames with the top n_leaders ratings and their rank for each latent feature
    '''
    return [get_n_leaders(ratings_df, column, n_leaders) for column in ratings_df.columns]
