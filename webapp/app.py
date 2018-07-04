import pandas as pd
import podrex_db_utils as db
import pickle
from random import shuffle
from flask import Flask, render_template, request, jsonify, g
from model import PodcastRecommender

app = Flask(__name__)

model = PodcastRecommender()
with open("podcast_pid_list.pickle", "rb") as in_pickle:
    podcast_pid_list = pickle.load(in_pickle)

def get_db():
    conn = getattr(g, '_database', None)
    if conn is None:
        conn = g._database = db.connect_db()
    return conn

def get_cards(indices):
    """
    Returns jsonified cards ready to send to browser

    Parameters:
    indices (list of ints): podcast integers corresponding to spark_pid column
    """
    conn = get_db()
    recommendation_data = db.get_podcast_info(conn, indices)
    #artid, title, sid, description, itunes, stitcher, podcast website
    cards = [{"art_id":result[0], "title":result[1], "sid":result[2],
              "description":result[3], "itunes_url":result[4],
              "stitcher_url":result[5], "podcast_url":result[6]}
             for result in recommendation_data]
    return cards

@app.route("/")
def index():
    """
    Returns home page to render to user
    """
    return render_template("index.html",
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
    if len(favorites) == 0 and len(thumbs) == 0:
        return "empty"
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
    if len(dismissed) <= 0:
        dismissed = None
    predictions = model.fit_predict(ratings, indices, dismissed)
    return jsonify(get_cards(predictions))

@app.route("/save_recommendations/", methods=["POST"])
def save_recommendations():
    """
    """
    unique_id = db.set_unique_page(conn, predictions) #  func to make unique id
    return unique_id

@app.route("/recommendations/")
def show_predictions():
    """
    Returns personalized recommendation page to the user.
    """
    likes = request.args.getlist("like")
    dismissed = request.args.getlist("dismissed")
    conn = get_db()
    try:
        indices = [int(like) for like in likes]
        ratings = [5 for podcast in range(len(indices))]
        dismissed = [int(dnl) for dnl in dismissed]
        predictions = model.fit_predict(ratings, indices, dismissed)
        cards = get_cards(predictions)
        return render_template("recommendations.html", cards=cards)
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
    return get_cards(results)

@app.teardown_appcontext
def close_connection(exception):
    conn = getattr(g, '_database', None)
    if conn is not None:
        conn.close()

def main():
    app.run(host="0.0.0.0", threaded=True)

if __name__ == "__main__":
    main()
