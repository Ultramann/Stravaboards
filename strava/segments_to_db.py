from pymongo import MongoClient
from strava_lib import get_segment_efforts

if __name__ == '__main__':
    client = MongoClient()
    db = client['Strava']
    table = db['Segment_Efforts']
    segments = [6366843, 617239, 904763, 1173191, 1723, 611363, 563888, 2386958, 3490822, 5264177, 626742, 8643847, 1154584, 3664904, 

    for segment in segments:
        for effort in get_segment_efforts(segment):
            if not table.find_one({'activity.id': effort['activity']['id']}):
                table.insert_one(effort)
