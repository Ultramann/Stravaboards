import pickle
from flask import Flask, render_template #, request
app = Flask(__name__)

@app.route('/')
@app.route('/leaderboards')
def display_leaderboards():
    # Unpickle leaderboard list
    lb_file_path = 'app_data/leaderboards.pkl'
    with open(lb_file_path, 'r') as f:
        df_leaderboards = pickle.load(f)

    # Turn df list into nparray list
    npa_leaderboards = [df_leaderboard.reset_index().values for df_leaderboard in df_leaderboards]

    # Make list of leaderboard lists with correct data types
    leaderboards = [[[int(row[0]), int(row[1]), round(float(row[2]), 3)] for row in leaderboard] 
                                                                for leaderboard in npa_leaderboards]

    return render_template('leaderboards.html', 
                            leaderboards_and_names=zip(leaderboards, 
                                                       ['Top', 'Second', 'Third', 'Last']))

if __name__ == '__main__':
    app.run(debug=True)
