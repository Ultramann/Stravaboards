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
    Input: Column from user latent feature (rating) matrix
    Output: Top n leaders and their ratings
    '''
    sorted_ratings_indexes = np.argsort(ratings_df[rating_column].values)
    top_n_indexes = sorted_ratings_indexes[-1:-n-1:-1]
    return ratings_df.loc[top_n_indexes][rating_column]
