import os
import discord
import time
import random
import sleep
from .text_game import Game


client = discord.Client(intents=discord.Intents.all())
new_command = False
latest_command = ""
channel = None
@client.event
async def on_ready():
    print('Logged in as: {0} - {1}'.format(client.user.name, client.user.id))
    print('-'*20)

# @client.event
# async def on_typing(channel, user, when):
#     print('Typing detected, sleeping for 3 seconds')
#     time.sleep(5.0)

@client.event
async def on_message(message):
    command = message.content
    # channel = message.channel
    
    print('-'*20)
    print(message)
    print(command)
    print('-'*20)

    if message.author == client.user:
        return
    elif command.startswith('!deku-text-game'):
        channel = message.channel
      #  newMessage = await message.channel.send(response)
        game = Game()
        game = game.start_game()
    elif command.startswith("!deku-command") and new_command is False:
        new_command = True

async def retrieve_discord_response():
    while new_command is False:
         sleep(1)
    new_command = False
    return latest_command.replace("!deku-command","")

def send_discord_message(text):
    channel.send(text)



token = os.getenv("DISCORD_TOKEN")
client.run(token)