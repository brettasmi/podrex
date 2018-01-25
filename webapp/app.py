from flask import Flask, render_template, request, jsonify

from model import Model

app = Flask(__name__)
m = Model()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict/', methods=['GET'])
def predict():
    preferences = ''
    predictions = m.predict(preferences)
    predictions = ' '.join([prediction for prediction in predictions])
    return predictions
if __name__ == '__main__':

    app.run(host='0.0.0.0', threaded=True)
