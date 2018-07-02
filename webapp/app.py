import pandas as pd
import podrex_db_utils as db
import pickle
from random import shuffle
from flask import Flask, render_template, request, jsonify, g
from model import PodcastRecommender

app = Flask(__name__)

model = PodcastRecommender()
with open("to_rate_list.pkl", "rb") as in_pickle:
    to_rate_list = pickle.load(in_pickle)
with open("podcast_pid_list.pickle", "rb") as in_pickle:
    podcast_pid_list = pickle.load(in_pickle)

def get_db():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = db.connect_db()
    return conn

@app.route("/")
def index():
    """
    Returns home page to render to user
    """
    shuffle(to_rate_list)
    return render_template("index.html", cards=to_rate_list,
                           podcasts=podcast_pid_list)

@app.route("/dd-update/", methods=["POST"])
def dropdown_update():
    """
    Returns data to update the dropdown card
    """
    user_input = request.json
    podcasts = []
    try:
        conn = get_db()
        podcasts.append(int(user_input["podcast"]))
        podcast_info = db.get_podcast_info(conn, podcasts)[0]
        podcast_json = jsonify(action="populate",
                               podcast_art_id=podcast_info[0],
                               podcast_name=podcast_info[1],
                               podcast_description=podcast_info[3])
        return podcast_json
    except ValueError:
        podcast_json = jsonify(action="destroy",
                               podcast_art_id="",
                               podcast_name="",
                               podcast_description="")
        return podcast_json

@app.route("/predictions/", methods=["POST"])
def predict():
    """
    Gets predictions from the model and returns html
    page and podcasts to render
    """
    conn = get_db()
    user_inputs = request.json
    favorites = user_inputs["favorites"]
    thumbs = user_inputs["thumbs"]
    dismissed = user_inputs["dismissed"]
    ratings, indices = [], []
    for k, v in thumbs.items():
        if v > 0:
            indices.append(int(k))
            ratings.append(int(v))
    for k, v in favorites.items():
        if k != "":
            try:
                pop_index = indices.index(int(k))
                indices.pop(pop_index)
                ratings.pop(pop_index)
            except ValueError:
                indices.append(int(k))
                ratings.append(5)
    dismissed = list({int(i) for i in dismissed})
    predictions = model.fit_predict(ratings, indices, dismissed)
    unique_id = db.set_unique_page(conn, predictions) #  func to make unique id
    return unique_id

@app.route("/recommendations/<unique_id>")
def show_predictions(unique_id):
    """
    Returns personalized recommendation page to the user.
    """
    conn = get_db()
    try:
        recommendations = db.get_prediction_info(conn, unique_id)
        return render_template("recommendations.html", cards=recommendations)
    except:
        return render_template("sorry.html")

@app.route("/about/")
def about_page():
    return render_template("about.html")

@app.route("/text-search/", methods=["POST"])
def text_search():
    """
    Returns recommendations based on a text-based search
    """
    search = request.json
    conn = get_db()
    model = PodcastRecommender()
    results = model.nlp_search(search["search"])
    recommendation_data = db.get_podcast_info(conn, results)
    #artid, title, sid, description, itunes, stitcher, podcast website
    cards = [{"art_id":result[0], "title":result[1], "sid":result[2],
              "description":result[3], "itunes_url":result[4],
              "stitcher_url":result[5], "podcast_url":result[6]}
             for result in recommendation_data]
    cards_json = jsonify(cards)
    return cards_json

@app.teardown_appcontext
def close_connection(exception):
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()

def main():
    app.run(host="0.0.0.0", threaded=True)

if __name__ == "__main__":
    main()
