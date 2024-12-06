#!/usr/bin/env python3

import asyncio
from twikit import Client
from dotenv import load_dotenv
import pandas as pd
import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
nltk.download('wordnet')
# from client_config import client

class TextPreprocessor:
    def __init__(self):
        # Initialize the word lemmatizer and the emojis dictionary
        self.word_lemmatizer = WordNetLemmatizer()
        self.emojis = {
            ":)": "smile",
            ":-)": "smile",
            ";d": "wink",
            ":-E": "vampire",
            ":(": "sad",
            ":-(": "sad",
            ":-<": "sad",
            ":P": "raspberry",
            ":O": "surprised",
            ":-@": "shocked",
            ":@": "shocked",
            ":-$": "confused",
            ":\\": "annoyed",
            ":#": "mute",
            ":X": "mute",
            ":^)": "smile",
            ":-&": "confused",
            "$_$": "greedy",
            "@@": "eyeroll",
            ":-!": "confused",
            ":-D": "smile",
            ":-0": "yell",
            "O.o": "confused",
            "<(-_-)>": "robot",
            "d[-_-]b": "dj",
            ":'-)": "sadsmile",
            ";)": "wink",
            ";D": "wink",
            ";-)": "wink",
            "O:-)": "angel",
            "O*-)": "angel",
            "(:-D": "gossip",
            "=^.^=": "cat",
            ":D": "smile",
            ":\\": "annoyed",
        }

    def clean_text(self, text):
        """Cleaning text from unwanted elements"""
        # Remove URLs
        text = re.sub(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", "", text)
        # Remove @username
        text = re.sub(r"@\w+", "", text).strip()
        # Remove email addresses
        text = re.sub(r"[\w\.\-\+]+@([\w\-]+\.)+[\w\-]{2,4}", "", text)
        # Remove quoted text
        text = re.sub(r'["\'].*?["\']', "", text)
        # Remove hashtags
        text = re.sub(r"#\w+", "", text)
        # Remove "etc."
        text = re.sub(r"\betc\.?\b", "", text, flags=re.IGNORECASE)

        return text

    def filter_non_english_words(self, text):
        """
        Remove all words that contain non-English characters.
        """
        pattern = r"\b(?:[a-zA-Z]+|EMOJI_[a-zA-Z_]+)\b"
        filtered = re.findall(pattern, text)
        return " ".join(filtered)

    def reduce_len_text(self, text):
        """Reduce text repetitive letters"""
        repeat_regexp = re.compile(r"(.)\1+")
        return repeat_regexp.sub(r"\1", text)

    def extract_features(self, text):
        """
        Extract features: link, mail, quote, etc...
        """
        return {
            "links": len(re.findall(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", text)),
            "emails": len(re.findall(r"[\w\.\-\+]+@([\w\-]+\.)+[\w\-]{2,4}", text)),
            "quotes": len(re.findall(r'["\'].*?["\']', text)),
            "hashtags": len(re.findall(r"#\w+", text)),
            "etc_count": len(re.findall(r"\betc\.?\b", text, flags=re.IGNORECASE)),
            "nb_caracter": len(text),
        }

    def lemmatize_text(self, text):
        """
        Lemmatize the words in the text.
        """
        processed_text = []
        for word in text.split():
            if len(word) > 1:
                lemmatized_word = self.word_lemmatizer.lemmatize(word)
                processed_text.append(lemmatized_word)
        return " ".join(processed_text)

    def handle_emojies(self, text):
        """Replace emojis with text"""
        for emoji, meaning in self.emojis.items():
            text = text.replace(emoji, "EMOJI_" + meaning)
        return text

    def preprocess(self, text):
        """
        Preprocess using all the previous functions
        """
        features = self.extract_features(text)

        cleaned_text = self.clean_text(text)
        replace_emojie = self.handle_emojies(cleaned_text)
        lemmatized_text = self.lemmatize_text(replace_emojie)
        no_repetition = self.reduce_len_text(lemmatized_text)
        clean = self.filter_non_english_words(no_repetition)
        return clean, features


def config():
    load_dotenv()


USERNAME = os.getenv("USERNAME")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# client = Client("en-US")

# async def login_agent():
#     """login to twitter"""
#     await client.login(auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD)
#     await login_agent()


async def get_tweets_async(topic, client):
    """Appel entièrement asynchrone pour récupérer les tweets."""
    tweets = await client.search_tweet(topic, "Latest")

    data = [
        {"username": tweet.user.name, "tweet": tweet.text, "date": tweet.created_at}
        for tweet in tweets
    ]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df


