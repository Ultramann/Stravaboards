import time
import eda_functions
from strava_db import EffortDfGetter

if __name__ == '__main__':
    t = time.time()
    df_getter = EffortDfGetter(origin='json')
    df = df_getter.get()
    print 'Retrieved dataframe with {} efforts in {:.2f} seconds'.format(df.shape[0], time.time()-t)

