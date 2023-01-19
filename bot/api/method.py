import requests

from bot import BEARER_TOKEN

s = requests.Session()
s.headers.update({'Authorization': f"Bearer {BEARER_TOKEN}"})

def get_tweet(id):
    return s.get(f"https://api.twitter.com/2/tweets/{id}?expansions=attachments.media_keys,author_id,referenced_tweets.id&media.fields=url,variants&user.fields=name&tweet.fields=entities").json()
