import os
import pandas as pd
from flask import Flask, render_template #, request
app = Flask(__name__)

# Make leaderboard list from csvs
app_data = './app_data/'
csv_list = os.listdir(app_data)
athlete_csv_list = [l for l in csv_list if 'athlete' in l]
segment_csv_list = [l for l in csv_list if 'segment' in l]

def get_np_board(csv_list):
    return [pd.read_csv(app_data + file_name).values for file_name in csv_list]

def get_boards(np_boards):
    return [[[int(row[0]), int(row[1]), round(float(row[2]), 3)] for row in board] 
              for board in np_boards]

def get_board_names(csv_list, board_name):
    return [name.strip('leaderboard.csv').strip(board_name).replace('_', ' ').title() 
            for name in csv_list]

@app.route('/')
def display_home():
    return render_template('home.html')

@app.route('/leaderboards')
def display_leaderboards():
    # Turn athlete csvs into dfs into nparray list
    np_leaderboards = get_np_board(athlete_csv_list)

    # Make list of leaderboard lists with correct data types
    leaderboards = get_boards(np_leaderboards)
    leaderboard_names = get_board_names(athlete_csv_list, 'athlete')

    return render_template('leaderboards.html', 
                            leaderboards_and_names=zip(leaderboards, leaderboard_names))

@app.route('/difficulty-boards')
def display_diffboards():
    # Turn athlete csvs into dfs into nparray list
    np_diffboards = get_np_board(segment_csv_list)

    # Make list of leaderboard lists with correct data types
    diffboards = get_boards(np_diffboards)
    diffboard_names = get_board_names(segment_csv_list, 'segment')

    return render_template('diffboards.html', 
                            diffboards_and_names=zip(diffboards, diffboard_names))

if __name__ == '__main__':
    app.run(debug=True)
