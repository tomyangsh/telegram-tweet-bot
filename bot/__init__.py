import tomli
import os

from pyrogram import Client

if not os.path.exists("config.toml"):
    print("config.toml is missing!")
    exit()

with open('config.toml', 'rb') as f:
    CONFIG = tomli.load(f)

bot = Client(**CONFIG['Telegram'])

BEARER_TOKEN = CONFIG['Twitter']['Bearer_Token']
