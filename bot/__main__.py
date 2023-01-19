import re, requests

from io import BytesIO

from bot import bot

from .api.type import Tweet

from pyrogram import filters
from pyrogram.types import InputMediaPhoto

async def send(chat_id, *content, disable_preview=False, reply_to=None):
    text = None
    image = None
    video = None
    image_set = None
    for i in content:
        if isinstance(i, str):
            if re.match('^http.+(jpg|jpeg|png)$', i):
                image = i
            elif re.match('^http.+mp4$', i):
                video = i
            else:
                text = i
        if isinstance(i, list):
            image_set = [InputMediaPhoto(BytesIO(requests.get(j).content)) for j in i]
    if image:
        return await bot.send_photo(chat_id, image, caption=text, reply_to_message_id=reply_to)
    elif video:
        try:
            return await bot.send_video(chat_id, video, caption=text, reply_to_message_id=reply_to)
        except:
            text += f" [Video]({video})"
            return await bot.send_message(chat_id, text, disable_web_page_preview=True, reply_to_message_id=reply_to)
    elif image_set:
        image_set[0].caption = text
        msg_list = await bot.send_media_group(chat_id, image_set, reply_to_message_id=reply_to)
        return msg_list[0]
    else:
        return await bot.send_message(chat_id, text, disable_web_page_preview=disable_preview, reply_to_message_id=reply_to)

async def process(chat_id, tweet, reply_to=None):
    disable_preview=True
    if not tweet.ok:
        return await send(chat_id, "Can't get tweet from a protected account", reply_to=reply_to)
    text = f"**{tweet.name}**"
    if tweet.extra_link:
        text += f"[\u200b]({tweet.extra_link})"
        disable_preview=False
    if tweet.text:
        text += f"\n{tweet.text}"
    if tweet.replied_to:
        msg = await process(chat_id, Tweet(tweet.replied_to), reply_to=reply_to)
        reply_to = msg.id
    if tweet.quote:
        text += "⬇"
    msg = await send(chat_id, text, tweet.image, tweet.video, disable_preview=disable_preview, reply_to=reply_to)
    if tweet.quote:
        await process(chat_id, Tweet(tweet.quote))
    return msg

async def tweet_link_filter(_, __, message):
    if message.text:
        return re.match('https://twitter.com/\w+/status/\d+.*', message.text)

tweet_link_filter = filters.create(tweet_link_filter)

@bot.on_message(filters.command('start'))
async def start(client, message):
    await send(message.chat.id, 'Send me a Tweet link (not profile link or anything else)\n\nTo know what else can this bot do, see [here](https://github.com/tomyangsh/telegram-tweet-bot#features)', disable_preview=True)

@bot.on_message(tweet_link_filter)
async def parse_tweet_link(client, message):
    tweet_id = re.match('https://twitter.com/\w+/status/(\d+).*', message.text).group(1)
    tweet = Tweet(tweet_id)
    await process(message.chat.id, tweet, reply_to=message.id)

bot.run()
