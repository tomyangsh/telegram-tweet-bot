import re

from .method import get_tweet

def by_bitrate(v):
    return v.get('bit_rate', -1)

class Tweet():
    def __init__(self, id):
        data = get_tweet(id)
        if not data.get('data'):
            self.ok = False
        else:
            self.ok =True
            self.id = id
            self.extra_link = ''
            text = data['data']['text']
            for i in data['data'].get('entities', {}).get('urls', []):
                if not re.match('https://twitter.com/.+', i['expanded_url']):
                    self.extra_link = i.get('unwound_url', i['expanded_url'])
                    domain = re.match('https?://(.+\.)?(.+)\..+', i.get('unwound_url', i['expanded_url'])).group(2).capitalize()
                    text = re.sub(i['url'], f"[{domain}]({i.get('unwound_url', i['expanded_url'])})", text)
                else:
                    text = re.sub(i['url'], '', text)
            for i in data['data'].get('entities', {}).get('mentions', []):
                text = re.sub(f"@{i['username']}", f"[@{i['username']}](https://twitter.com/{i['username']})", text)
            self.text = text
            self.name = data['includes']['users'][0]['name']
            self.username = data['includes']['users'][0]['username']
            self.link = f"https://twitter.com/{self.username}/status/{id}"
            self.quote = None
            self.replied_to = None
            for i in data['data'].get('referenced_tweets', []):
                if i['type'] == 'quoted':
                    self.quote = i['id']
                else:
                    self.replied_to = i['id']
            self.image = []
            self.video = None
            for i in data['includes'].get('media', []):
                if i['type'] == 'photo':
                    self.image.append(i['url'])
                elif i['type'] == 'video' or i['type'] == 'animated_gif':
                    i['variants'].sort(key=by_bitrate)
                    self.video = re.match('http.+mp4', i['variants'][-1]['url']).group(0)
            if len(self.image) == 1:
                self.image = self.image[0]
            elif not self.image:
                self.image = None
