#!/usr/bin/env python3
from flask import Flask, render_template, request
import joblib
from scrapping import get_tweets, initialize_client, TextPreprocessor
from flask.cli import AppGroup
import pandas as pd
import asyncio

app = Flask(__name__)

tfidf_vectorizer = joblib.load("model/TF-IDF Vector.pkl")
sentiment_model = joblib.load("model/LR sentiment analysis.joblib")
pre = TextPreprocessor()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = loop.run_until_complete(initialize_client())
client.load_cookies('cookies.json')

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_data():
    topic = request.form.get("topic")
    if not topic:
        return render_template("index.html", error="Please enter a topic.")

    try:
        df = loop.run_until_complete(get_tweets(topic, client))
        if df.empty:
            return render_template("index.html", error="No tweets found for the topic.")
    except Exception as e:
        return render_template("index.html", error=f"Error fetching tweets: {e}")

    df["cleaned_tweets"] = df["tweet"].apply(pre.preprocess)
    tfidf_matrix = tfidf_vectorizer.transform(df["cleaned_tweets"])
    df['sentiment'] =  sentiment_model.predict(tfidf_matrix)
    positive_per = (df["sentiment"] == 1).mean() * 100
    negative_per = (df["sentiment"] == 0).mean() * 100
    tweets_html = df.to_html(index=False, classes="tweets-table")
    return render_template(
        "index.html",
        data=tweets_html,
        topic=topic,
        positive_percentage=positive_per,
        negative_percentage=negative_per,
    )


if __name__ == "__main__":
    app.run()
