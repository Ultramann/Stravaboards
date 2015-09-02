from pymongo import MongoClient
from multiprocessing import Pool
from strava_lib import get_segment_efforts

def get_insert_segment_efforts(segment):
    efforts = get_segment_efforts(segment)
    for effort in efforts:
        if (isinstance(effort, dict) and isinstance(effort['activity'], dict)):
            if not table.find_one({'activity.id': effort['activity']['id']}):
                table.insert_one(effort)


if __name__ == '__main__':
    client = MongoClient()
    db = client['Strava']
    table = db['Segment_Efforts']
    segments = [1173191, 1723, 611363, 563888, 2386958, 3490822, 5264177, 
                626742, 8643847, 1154584, 3664904, 7330795, 809335, 857898, 954038, 600237, 1262370,
                1549153, 954038, 618199, 1741438, 719341, 638232, 949453, 997901, 3883126, 7197693]
    finished_segments = [6366843, 617239, 904763]

    pool = Pool(processes=2)
    pool.map(get_insert_segment_efforts, segments)
