import os
import pandas as pd
from flask import Flask, render_template #, request
app = Flask(__name__)

@app.route('/')
@app.route('/leaderboards')
def display_leaderboards():
    # Make leaderboard list from csvs
    app_data = './app_data/'
    csv_list = os.listdir(app_data)

    # Turn csvs into dfs into nparray list
    np_leaderboards = [pd.read_csv(app_data + file_name).values for file_name in csv_list]

    # Make list of leaderboard lists with correct data types
    leaderboards = [[[int(row[0]), int(row[1]), round(float(row[2]), 3)] 
                      for row in leaderboard] 
                     for leaderboard in np_leaderboards]

    leaderboard_names = [name[:-16].replace('_', ' ').title() for name in csv_list]
    return render_template('leaderboards.html', 
                            leaderboards_and_names=zip(leaderboards, leaderboard_names))

if __name__ == '__main__':
    app.run(debug=True)
