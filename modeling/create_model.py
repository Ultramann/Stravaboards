import graphlab as gl
import pandas as pd

# Types of segments to classify
subset_querys_dict = {'total': None, 
                      'uphill': 'seg_average_grade > 0', 
                      'downhill': 'seg_average_grade < 0'}
    
def get_agg_sf(df):
    '''
    Input: DataFrame with data to create model from
    Output: SFrame of target data aggregated over athlete-segment pairs
    '''
    # Columns that are going to be used to make model
    columns_to_keep = ['segment_id', 'athlete_id', 'average_speed']

    # Take mean over aggregated athlete-segment pairs, move those columns out of index
    agg_df = df.groupby(['athlete_id', 'segment_id']).mean().reset_index()

    # Return an SFrame of those aggregated target column, average_speed
    return gl.SFrame(agg_df[columns_to_keep])

def make_cleaner_dfs(dfs, num_features):
    '''
    Input: List of DataFrames with latent features in single list, how many latent features in list
    Output: List of DataFrames with the latent features in seperate columns 
    '''
    # For each dataframe make a new column, with rating_* as name, for each latent feature
    return [pd.concat([df] + [pd.Series(df.factors.apply(lambda x: x[i]), 
                              name='rating_{}'.format(i+1)) for i in range(num_features)],
                      axis=1)  for df in dfs]

def drop_useless_columns(dfs):
    '''
    Input: List of DataFrames
    Output: None

    Get rid of the columns that were turned into individual columns or were never useful
    '''
    for df in dfs:
        df.drop(['factors', 'linear_terms'], axis=1, inplace=True)

def get_clean_dfs_from_model(model, num_features):
    '''
    Input: Fitted GraphLab recommender model, number of features the model decomposed date into
    Output: DataFrame of athlete ratings from model, DataFrame of segment ratings from model
    '''
    # Get dictionary of model coefficients
    model_coefficients = model['coefficients']

    # Turn the athlete and segment coefficients into dataframes
    athlete_df = model_coefficients['athlete_id'].to_dataframe()
    segment_df = model_coefficients['segment_id'].to_dataframe()

    # Clean up dataframes by moving latent features from list into separate columns
    cleaner_athlete_df, cleaner_segment_df = make_cleaner_dfs([athlete_df, segment_df], num_features)

    # Get rid of columns that wont be of use
    drop_useless_columns([cleaner_athlete_df, cleaner_segment_df])

    # Reset indices
    cleaner_athlete_df.set_index(['athlete_id'], inplace=True)
    cleaner_segment_df.set_index(['segment_id'], inplace=True)

    return cleaner_athlete_df, cleaner_segment_df

def get_latent_features(agg_sf, number_latent_features):
    '''
    Input: SFrame of data aggregated over athlete-segment pairs to be modeled,
           Number of latent features in unitary matricies
    Output: DataFrame of athlete_ratings, DataFrame of segment_ratings, Fitted GraphLab model
    '''
    # Make and fit GraphLab model to agg_sf data
    model = gl.factorization_recommender.create(agg_sf, user_id='athlete_id', item_id='segment_id', 
                                                target='average_speed', 
                                                regularization=0,
                                                linear_regularization=0,
                                                solver='sgd',
                                                max_iterations=100,
                                                num_factors=number_latent_features)
    # Turn fitted model into athlete_ratings df and segment_ratings df
    athlete_ratings, segment_ratings = get_clean_dfs_from_model(model, number_latent_features)

    return athlete_ratings, segment_ratings, model

def get_dfs_for_model(df, segment_type_names):
    '''
    Input: Full DataFrame for total model, list of subset types to return
    Output: Dictionary of subset name, corresponding subsetted df pairs
    '''
    # Get dictionary of queried df, by query string if query string is present, otherwise total df
    return {name: df.query(subset_querys_dict[name]) if subset_querys_dict[name] else df 
            for name in segment_type_names}

def get_sfs_for_model(df, segment_type_names):
    '''
    Input: Full DataFrame to be subsetted and turned into SFrames from modeling, list of subset types
           to return
    Output: Dictionary of subset name, corresponding subsetted sf pairs
    '''
    # Get subsetted dfs for model dict
    dfs_for_model = get_dfs_for_model(df, segment_type_names)
    return {name: get_agg_sf(df) for name, df in dfs_for_model.items()}

def df_to_latent_features(df, number_latent_features=1, 
                          segment_type_names = ['total', 'uphill', 'downhill']):
    '''
    Input: DataFrame with observations for model to be trained on, 
           Number of latent features for model to decompose data into
    Output: DataFrame of athlete_ratings, DataFrame of segment_ratings, Fitted GraphLab model
    '''
    # Get all the SFrames for the subsets of the df corresponding with types list
    sfs_for_model = get_sfs_for_model(df, segment_type_names)

    # Get all ratings dfs and models in a dictionary
    rankings_dict = {name: get_latent_features(sf, number_latent_features) 
                     for name, sf in sfs_for_model.items()}
    
    # Make aggregate rankings dfs by concatenating rankings from all models together
    athlete_ratings = pd.concat([pd.Series(rankings_dict[name][0].rating_1, 
                                           name='{}_rating'.format(name))
                                 for name in segment_type_names], 
                                axis=1)
    segment_ratings = pd.concat([pd.Series(rankings_dict[name][1].rating_1, 
                                           name='{}_rating'.format(name))
                                 for name in segment_type_names], 
                                axis=1)

    # Make dictionary of models for each segment type
    models = {name: rankings_dict[name][2] for name in segment_type_names}

    return athlete_ratings, segment_ratings, models
