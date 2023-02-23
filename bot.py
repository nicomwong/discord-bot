import discord
import random

with open("token", "r") as tokenFile:
    TOKEN = tokenFile.read()

happy_messages = [
    "Yay! That's great to hear!",
    "Awesome!",
    "You made my day!",
    "So happy for you!",
    "Hooray!",
    "That's fantastic news!"
]


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'{client.user} is now running!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    channel = str(message.channel)

    if channel != "bot":
        return

    await message.channel.send(random.choice(happy_messages))

client.run(TOKEN)
