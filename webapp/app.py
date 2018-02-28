import pandas as pd
import podrex_db_utils as db
import pickle
from random import shuffle
from flask import Flask, render_template, request, jsonify
from model import PodcastRecommender

app = Flask(__name__)

model = PodcastRecommender()
with open("to_rate_list.pkl", "rb") as in_pickle:
    to_rate_list = pickle.load(in_pickle)
with open("podcast_pid_list.pickle", "rb") as in_pickle:
    podcast_pid_list = pickle.load(in_pickle)

conn, cursor = db.connect_db()

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
        podcasts.append(int(user_input["podcast"]))
        podcast_info = db.get_podcast_info(conn, podcasts)[0]
        #print(podcast_info)
        podcast_json = jsonify(action="populate",
                               podcast_art_id=podcast_info[0],
                               podcast_description=podcast_info[3])
        return podcast_json
    except ValueError:
        podcast_json = jsonify(action="destroy",
                               podcast_art_id="",
                               podcast_description="")
        return podcast_json
        
@app.route("/predictions/", methods=["POST"])
def predict():
    """
    Gets predictions from the model and returns html
    page and podcasts to render
    """
    user_inputs = request.json
    parameters = user_inputs["parameters"]
    checkboxes = user_inputs["checkboxes"]
    favorites = user_inputs["favorites"]
    ratings, indices = [], []
    #print(parameters, checkboxes, favorites)
    for k, v in parameters.items():
        if v > 0:
            indices.append(int(k))
            ratings.append(int(v))
    #print(indices, ratings)
    for k, v in checkboxes.items():
        if v:
            try:
                pop_index = indices.index(int(k))
                indices.pop(pop_index)
                ratings.pop(pop_index)
            except ValueError:
                indices.append(int(k))
                ratings.append(0.1)
    for k, v in favorites.items():
        if k != "":
            try:
                pop_index = indices.index(int(k))
                indices.pop(pop_index)
                ratings.pop(pop_index)
            except ValueError:
                indices.append(int(k))
                ratings.append(5)
    #print(indices, ratings)
    predictions = model.fit_predict(ratings, indices)
    unique_id = db.set_unique_page(conn, cursor, predictions) # write func to make unique id
    return unique_id


@app.route("/recommendations/<unique_id>")
def show_predictions(unique_id):
    """
    Returns personalized recommendation page to the user.
    """
    try:
        recommendations = db.get_prediction_info(conn, cursor, unique_id)
        return render_template("recommendations.html", cards=recommendations)
    except:
        return render_template("sorry.html")
def main():
    app.run(host="0.0.0.0", threaded=True)

if __name__ == "__main__":
    main()
