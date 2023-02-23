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

    prompt = str(message.content)

    api_response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=256,
        temperature=0
    ).choices[0].text

    response = "I am an OpenAI AI model.\nQuery: \"{}\"\nResponse: {}\"".format(
        prompt, api_response)

    print(response)

    await message.channel.send(response)

client.run(TOKEN)
