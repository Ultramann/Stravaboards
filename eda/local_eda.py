import time
import eda_fuctions
from strava_db import EffortDfGetter

if __name__ == '__main__':
    t = time.time()
    df_getter = EffortDfGetter(origin='mongo')
    df = df_getter.get(300000)
    print 'Retrieved dataframe with {} efforts in {:.2f} seconds'.format(df.shape[0], time.time()-t)




# Random mongo searches for stats
    # Number of athletes with > 5 efforts
    '''
    db.segment_efforts.aggregate( [ 
    { 
      $group: { 
                _id: '$athlete.id', 
                total_eff: { $sum: 1 } 
              } 
    }, 
    { 
      $match: { 
                total_eff: { $gt: 5 } 
              } 
    },
    {
      $group: {
                _id: '$_id.total_eff',
                count: { $sum: 1 }
              }
    } ] )
    '''
