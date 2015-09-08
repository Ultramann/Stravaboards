import seaborn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def print_num_atheletes_with_efforts_gt(df, nums):
    for num in nums:
        num_aths = len(df.groupby('athlete_id').count().query('activity >= {}'.format(num)))
        print 'Number of athletes with greater than {} efforts in the database: {}'.format(
                                                                                num, num_aths)

def plot_num_athletes_by_effort_count_hist(df, 
                       bin_list=[1, 2, 4, 6, 8, 10, 12, 14, 16, 26, 51, 101, 100000], 
                       bin_labels=['1', '2-3', '4-5', '6-7', '8-9', '10-11', '12-13', '14-15',
                                   '16-25', '26-50', '51-100', '101+'],
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
    ax.set_xticklabels(bin_labels, rotation=25)
    if not show:
        plt.close()
    if save and file_name:
        fig.savefig(file_name)

def plot_num_activities_by_effort_count_hist(df, bin_list=[1, 2, 4, 6, 8, 10, 12, 100000],
                             bin_labels=['1', '2-3', '4-5', '6-7', '8-9', '10-11', '12+'],
                             show=True, save=False, file_name=None):
    counts_by_activity = pd.Series(df.groupby('activity_id').count().date, name='effort_count')
    count_series = counts_by_activity.groupby(pd.cut(counts_by_activity, bin_list, 
                                                     labels=bin_labels)).count()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    count_series.plot(kind='bar', axes=ax, grid=False)
    plt.xlabel('Number of efforts in database')
    plt.ylabel('Number of activites')
    plt.title('Activities by effort count')
    ax.set_xticklabels(bin_labels, rotation=25)
    if not show:
        plt.close()
    if save and file_name:
        fig.savefig(file_name)
