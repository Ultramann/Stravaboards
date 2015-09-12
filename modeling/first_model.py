import sys
sys.path.append('../eda')
from strava_db import EffortDfGetter
import validate_model as vm
import create_model as cm

def get_df():
    df_getter = EffortDfGetter(origin='json')
    return df_getter.get()

if __name__ == '__main__':
    df = get_df()
    training_df, testing_df = vm.split_efforts(df)
    athlete_ratings, segment_ratings, model = cm.df_to_latent_features(training_df, 2)
