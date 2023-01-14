import csv
import os
import shutil
import urllib

import numpy as np
import spacy as spacy
from flask import Flask
from flask_cors import CORS, cross_origin
from spacy.language import Language
from spacy_langdetect import LanguageDetector
from flask import request
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import warnings

warnings.simplefilter("ignore")
app = Flask(__name__)
CORS(app)

path = "cardiffnlp"
if os.path.exists(path):
    shutil.rmtree(path)

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"

tokenizer = AutoTokenizer.from_pretrained(MODEL)

# download label mapping
labels = []
mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/sentiment/mapping.txt"
with urllib.request.urlopen(mapping_link) as f:
    html = f.read().decode('utf-8').split("\n")
    csvreader = csv.reader(html, delimiter='\t')
labels = [row[1] for row in csvreader if len(row) > 1]

model = AutoModelForSequenceClassification.from_pretrained(MODEL)
model.save_pretrained(MODEL)


def preprocess(text):
    new_text = []

    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)


# @Language.factory("language_detector")
def get_lang_detector(nlp, name):
    return LanguageDetector()


def spacy_language_detection(text, model):
    pipeline = list(dict(model.pipeline).keys())

    if (not "language_detector" in pipeline):
        Language.factory("language_detector", func=get_lang_detector)
        model.add_pipe("language_detector", last=True)

    doc = model(text)
    return doc._.language


@app.route("/")
def hello():
    return "<h1>Not Much Going On Here</h1>"


@app.route("/api/language-detection", methods=["POST"])
def detectLanguage():
    print("detected 1")
    tweets = request.get_json()
    pre_trained_model = spacy.load("en_core_web_sm")
    for tweet in tweets:
        tweet["is_english"] = spacy_language_detection(tweet["tweet_text"], pre_trained_model)['language'] == "en"
    print("detected")
    return tweets


@app.route("/api/sentiment-score", methods=["POST"])
@cross_origin()
def getSentimentScore():
    tweets = request.get_json()
    for tweet in tweets:
        tweet_text = preprocess(tweet["tweet_text"])
        encoded_input = tokenizer(tweet_text, return_tensors='pt')
        output = model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        print("scores")
        print(scores)

        score_result = {}
        score_result["positive"] = str(scores[2])
        score_result["neutral"] = str(scores[1])
        score_result["negative"] = str(scores[0])
        tweet["sentiment_score"] = score_result

        ranking = np.argsort(scores)
        # ranking = ranking[::-1]
        tweet["detected_mood"] = str(labels[ranking[2]]).upper()
        # for i in range(scores.shape[0]):
        #     if(ranking[i] == 0):
        #         tweet["detected_mood"] = labels[ranking[i]]
        #     l = labels[ranking[i]]
        #     s = scores[ranking[i]]
        #     print(f"{i + 1}) {l} {np.round(float(s), 4)}")

        print(tweet)
    return tweets


app.run(host='0.0.0.0', port=50000)
