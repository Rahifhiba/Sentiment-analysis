#!/usr/bin/env python3
from flask import Flask, render_template, request
import joblib
from scrapping import *
from twikit import Client
from dotenv import load_dotenv
import os
import asyncio
from client_config import client


app = Flask(__name__)
tfidf_vectorizer = joblib.load("model/TF-IDF Vector.pkl")
sentiment_model = joblib.load("model/LR sentiment analysis.joblib")
pre = TextPreprocessor()


# Load environment variables
def config():
    load_dotenv()


config()

# USERNAME = os.getenv("USERNAME")
# EMAIL = os.getenv("EMAIL")
# PASSWORD = os.getenv("PASSWORD")


# client = Client("en-US")
# client.login(auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD)
# print("login succeeded")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
async def analyze_sentiment():
    topic = request.form.get("topic")
    if not topic:
        return render_template("index.html", error="No topic provided")
    # try:
    df = await get_tweets_async(topic, client)  # Fetch tweets asynchronously
    tweets_data = df.to_dict(
        orient="records"
    )  # Convert DataFrame to a list of dictionaries
    return render_template("index.html", tweets=tweets_data, topic=topic)
    # except Exception as e:
    #     return render_template("index.html", error=f"Error fetch tweets: {e}")


if __name__ == "__main__":
    # asyncio.run(login_agent())  # Ensure login before starting the server
    app.run(debug=True)
