import pandas as pd
from pymongo import MongoClient

def get_activities():
    client = MongoClient()
    db = client['Strava']
    table = db['Bozeman_efforts']
    df = pd.DataFrame(list(table.find()))
    df['activity_id'] = df.activity.apply(lambda x: x['id'])
    return df.activity_id.unique()

if __name__ == '__main__':
    activities = get_activities()
    
