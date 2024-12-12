#!/usr/bin/env python3
import contractions
import asyncio
from twikit import Client
from dotenv import load_dotenv
import pandas as pd
import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import re
import emoji
# nltk.download("wordnet")
# from client_config import client


class TextPreprocessor:
    def __init__(self):
        # Initialize the word lemmatizer and the emojis dictionary
        self.word_lemmatizer = WordNetLemmatizer()
        self.emojis = {
            ':)': 'smile',
             ':-)': 'smile',
             ';d': 'wink',
             ':-E': 'vampire',
             ':(': 'sad',

            ':-(': 'sad',
             ':-<': 'sad',
             ':P': 'raspberry',
             ':O': 'surprised',

            ':-@': 'shocked',
             ':@': 'shocked',
            ':-$': 'confused',
             ':\\': 'annoyed',

            ':#': 'mute',
             ':X': 'mute',
             ':^)': 'smile',
             ':-&': 'confused',
             '$_$': 'greedy',

            '@@': 'eyeroll',
             ':-!': 'confused',
             ':-D': 'smile',
             ':-0': 'yell',
             'O.o': 'confused',

            '<(-_-)>': 'robot',
             'd[-_-]b': 'dj',
             ":'-)": 'sad smile',
             ';)': 'wink',
             ';D': 'wink',

            ';-)': 'wink',
             'O:-)': 'angel',
            'O*-)': 'angel',
            '(:-D': 'gossip',
             '=^.^=': 'cat',
             ':D':'smile',
        }

    def clean_text(self, text):
        """Cleaning text from unwanted elements"""
        text = text.lower().strip()
        text = contractions.fix(text)
        # Remove URLs
        text = re.sub(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', '', text)
        # Remove @username
        text = re.sub(r'@\w+', '', text).strip()
        # Remove email addresses
        text = re.sub(r'[\w\.\-\+]+@([\w\-]+\.)+[\w\-]{2,4}', '', text)
        # Remove quoted text
        text = re.sub(r'["\'].*?["\']', '', text)
        # Remove hashtags
        text = re.sub(r'#(\w+)', r'\1', text)
        # Remove "etc."
        text = re.sub(r'\betc\.?\b', '', text, flags=re.IGNORECASE)
        return text

    def filter_non_english_words(self, text):
        """
        Remove all words that contain non-English characters.
        """
        pattern = r'\b(?:[a-zA-Z]+|[a-zA-Z_]+)\b'
        filtered = re.findall(pattern, text)
        return ' '.join(filtered)

    def reduce_len_text(self, text):
        """Reduce text repetitive letters """
        repeat_regexp = re.compile(r'(.)\1{2,}')
        return repeat_regexp.sub(r'\1', text)

    def lemmatize_text(self, text):
        return ' '.join(self.word_lemmatizer.lemmatize(word) for word in text.split())
    def handle_emojies(self, text):
        """Replace emojis with text"""
        text = emoji.demojize(text, delimiters=(" ", " "))
        for e, meaning in self.emojis.items():
            text = text.replace(e, meaning)
        return text

    def preprocess(self, text):
        """
        Preprocess using all the previous functions
        """
        # features = self.extract_features(text)

        replace_emojie = self.handle_emojies(text)
        cleaned_text = self.clean_text(replace_emojie)
        no_repetition = self.reduce_len_text(cleaned_text)
        lemmatized_text = self.lemmatize_text(no_repetition)
        clean = self.filter_non_english_words(lemmatized_text)
        return clean

load_dotenv()


USERNAME = os.getenv("USERNAME")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

if not USERNAME or not EMAIL or not PASSWORD:
    raise ValueError("Ensure USERNAME, EMAIL, and PASSWORD are set in your .env file")
client = Client("en-US")

async def initialize_client():
    """Initialise le client Twikit avec la boucle actuelle."""
    client = Client("en-US")
    await client.login(auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD)
    client.save_cookies("cookies.json")
    return client



# async def get_tweets(topic, client, lang="en", max_tweet=100):
#     tweets = await client.search_tweet(topic, 'Latest')
#     more_user_tweets = await tweets.next()
#     data = []
#     for tweet in more_user_tweets:
#         if tweet.lang == lang:
#             data.append(
#                 {"username" :tweet.user.name,
#                 "tweet": tweet.text,
#                 "date": tweet.created_at}
#             )
#     df = pd.DataFrame(data)
#     df['date'] = pd.to_datetime(df['date'], errors='coerce')
#     df['date'].dropna(inplace=True)
#     df['tweet'].dropna(inplace=True)
#     return df


async def get_tweets(topic, client, lang="en", max_tweet=10000):
    tweets = await client.search_tweet(topic, "Latest")  # Initiate the search
    data = []

    while len(data) < max_tweet:  # Continue until we reach the desired count
        try:
            more_user_tweets = await tweets.next()  # Fetch the next page
            if not more_user_tweets:  # Break if no more tweets are available
                break

            for tweet in more_user_tweets:
                if tweet.lang == lang:
                    data.append(
                        {
                            "username": tweet.user.name,
                            "tweet": tweet.text,
                            "date": tweet.created_at,
                        }
                    )
                    if len(data) >= max_tweet:  # Stop if we hit the limit
                        break

        except Exception as e:  # Handle errors, e.g., rate limits or connection issues
            print(f"Error fetching tweets: {e}")
            break

    # Convert to DataFrame and clean up
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "tweet"])  # Drop rows with missing date or tweet
    return df
