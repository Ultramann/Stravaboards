import os
import pandas as pd
from flask import Flask, render_template #, request
app = Flask(__name__)

@app.route('/')
@app.route('/leaderboards')
def display_leaderboards():
    # Make leaderboard list from csvs
    app_data = '../app_data/'
    csv_list = os.listdir(app_data)
    leaderboards = [pd.read_csv(app_data + file_name) for file_name in csv_list]

    # Turn df list into nparray list
    #npa_leaderboards = [df_leaderboard.reset_index().values for df_leaderboard in df_leaderboards]

    # Make list of leaderboard lists with correct data types
    #leaderboards = [[[int(row[0]), int(row[1]), round(float(row[2]), 3)] for row in leaderboard] 
    #                                                            for leaderboard in npa_leaderboards]

    return render_template('leaderboards.html', 
                            leaderboards_and_names=zip(leaderboards, 
                                                       [name[:-13] for name in csv_list]))

if __name__ == '__main__':
    app.run(debug=True)
