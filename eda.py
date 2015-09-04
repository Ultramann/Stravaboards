import time
import seaborn
import pandas as pd
import matplotlib.pyplot as plt
from strava_db import get_clean_df

def print_num_atheletes_with_efforts_gt(df, nums):
    for num in nums:
        num_aths = len(df.groupby('athlete_id').count().query('activity >= {}'.format(num)))
        print 'Number of athletes with greater than {} efforts in the database: {}'.format(
                                                                                num, num_aths)
def plot_num_athletes_by_effort_count_hist(df, bin_list=[1, 2, 3, 4, 11, 26, 51, 101, 100000], 
                       bin_labels=['1', '2', '3', '4-10', '11-25', '26-50', '51-100', '101+'],
                       show=True, save=False, file_name=None):
    counts_by_athlete = pd.Series(df.groupby('athlete_id').count().date, name='effort_count')
    count_series = counts_by_athlete.groupby(pd.cut(counts_by_athlete, bin_list, 
                                                    labels=bin_labels)).count()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    count_series.plot(kind='bar', axes=ax, grid=False)
    plt.xlabel('Number of efforts in database')
    plt.ylabel('Number of athletes')
    plt.title('Athletes by effort count')
    ax.set_xticklabels(bin_labels, rotation=0)
    if not show:
        plt.close()
    if save and file_name:
        fig.savefig(file_name)

if __name__ == '__main__':
    t = time.time()
    df = get_clean_df()
    print 'Retrieved dataframe with {} efforts in {:.2f} seconds'.format(df.shape[0], time.time()-t)
