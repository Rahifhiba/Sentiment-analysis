#!/usr/bin/env python3
from flask import Flask, render_template, request
import joblib
from scrapping import get_tweets, initialize_client
from flask.cli import AppGroup
import pandas as pd
import asyncio

app = Flask(__name__)

tfidf_vectorizer = joblib.load("model/TF-IDF Vector.pkl")
sentiment_model = joblib.load("model/LR sentiment analysis.joblib")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = loop.run_until_complete(initialize_client())



@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_data():
    topic = request.form.get("topic")
    if not topic:
        return render_template("index.html", error="Please enter a topic.")

    try:
        tweets_data = loop.run_until_complete(get_tweets(topic, client))
        if tweets_data.empty:
            return render_template("index.html", error="No tweets found for the topic.")
    except Exception as e:
        return render_template("index.html", error=f"Error fetching tweets: {e}")
    
    tweets_html = tweets_data.to_html(index=False, classes="tweets-table")
    return render_template("index.html", data=tweets_html, topic=topic)


if __name__ == "__main__":
    app.run()
