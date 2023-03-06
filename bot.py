import discord
import openai
import os

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

with open("token", "r") as tokenFile:
    TOKEN = tokenFile.read()

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
    if str(message.channel) != "bot":
        return

    chatMessage = str(message.content)

    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": chatMessage}
        ],
        max_tokens=512
    ).choices[0].message.content

    print(chatMessage)
    print(api_response)

    await message.channel.send(api_response)

client.run(TOKEN)
