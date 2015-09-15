import numpy as np
import pandas as pd

class Leaderboards(object):
    def __init__(self, average_speeds):
        '''
        Input:  Pandas Series of average speed for each athlete
        '''
        self.average_speeds = average_speeds

    def store(self, ratings_df, board_size=20):
        '''
        Input:  DataFrame of ratings, size of leaderboards
        Output: None
        
        Store each of the leaderboards from the leaderboard list from get in app_data folder as csvs
        '''
        leaderboards = self.get(ratings_df, board_size)
        for key in leaderboards.keys():
            leaderboards[key].to_csv('../app/app_data/{}_leaderboard.csv'.format(key))

    def get(self, ratings_df, board_size=20):
        '''
        Input:  DataFrame of ratings, size of leaderboards
        Output: List of DataFrames with the top n_leaders ratings and their rank 
                for each latent feature
        '''
        # Store the Dataframe of ratings and requested leaderboard size
        self.ratings = ratings_df
        self.board_size = -1 if board_size == 'all' else board_size

        # Make scaled ratings df
        self.scaled_ratings = ratings_df.copy(deep=True)
        for column in self.ratings.columns:
            self.scale_column_ratings(column)

        # Make leaderboard dict
        leaderboards = {column: self.get_n_leaders(column) for column in self.ratings.columns}

        return leaderboards

    def get_n_leaders(self, rating_column):
        '''
        Input: Column from user latent feature (rating) matrix
        Output: DataFrame of top n leaders and their ratings for input column
        '''
        # Get the indicies of the sorted scaled ratings
        sorted_scaled_ratings_indices = np.argsort(self.scaled_ratings[rating_column].values)

        # We only want the top n athletes for the leaderboard
        top_n_indices = sorted_scaled_ratings_indices[-1:-self.board_size-1:-1]
        
        # Grab the top n athletes and there rating_column stats
        n_leaders = self.scaled_ratings.iloc[top_n_indices][rating_column]
        n_leaders_df = n_leaders.reset_index()

        # Make new column, rank, ranging from 1 - n
        worst_rank = n_leaders_df.shape[0] if self.board_size == -1 else self.board_size
        n_leaders_df['rank'] = range(1, self.board_size+1)

        # Set it to be the index
        n_leaders_df.set_index('rank', inplace=True)

        return n_leaders_df

    def scale_column_ratings(self, rating_column):
        '''
        Input: DataFrame of latent features (ratings)
        Output: Copy of ratings 

        Scales ratings from current to 0 - 100, by column
        '''
        # Athletes in column
        athletes = self.scaled_ratings[pd.notnull(self.scaled_ratings[rating_column])].index

        # Make np array of those athletes columns ratings
        scaled_ratings_column = self.scaled_ratings.ix[athletes][rating_column]
    
        # Figure out the orentation of ratings scale
        correlation_matrix = np.corrcoef(scaled_ratings_column, self.average_speeds[athletes].values)
        orientation = 1 if correlation_matrix[0][1] < 0 else -1

        # Make sure that the ratings are correctly oriented
        scaled_ratings_column *= orientation

        # Add the magnitude of the minimum rating to all, columnwise
        scaled_ratings_column -= scaled_ratings_column.min()

        # Multiply by the ratio of 100:(new max rating), columnwise
        scaled_ratings_column *= 100. / scaled_ratings_column.max() 

        # Set the newly scaled column values back into the scaled df
        self.scaled_ratings[rating_column] = scaled_ratings_column
        self.scaled_ratings[rating_column].fillna(-1, inplace=True)
