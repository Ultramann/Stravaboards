import numpy as np

def scale_ratings(ratings_df):
    '''
    Input: DataFrame of latent features (ratings)
    Output: None

    Scales ratings from current to 0 - 100, by column
    '''
    # Make cope of ratings df to scale
    scaled_ratings_df = ratings_df.copy(deep=True)

    # Add the magnitude of the minimum rating to all, columnwise
    scaled_ratings_df += abs(ratings_df.min())

    # Multiply by the ratio of 100:(new max rating), columnwise
    scaled_ratings_df *= 100. / ratings_df.max() 

    return scaled_ratings_df
    
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
