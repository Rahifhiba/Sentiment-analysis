from dotenv import load_dotenv
from twikit import Client
import os
import asyncio

load_dotenv()

USERNAME = os.getenv("USERNAME")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


async def initialize_client():
    client = Client("en-US")
    await client.login(auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD)
    return client


# Exécuter la configuration et stocker `client`
client = asyncio.run(initialize_client())
