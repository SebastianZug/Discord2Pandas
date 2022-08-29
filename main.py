# This script parses multiple discord channels and categories. It
# extracts all messages and provides three pandas files finally:
# - category_list    : Cluster names structuring channel lists
# - textmessage_list : Contains all message content, authors and 
#                      timestamps + references on channel ids 
# - textchannel_list : Individual channel parameter 
#
# The configuration of a discord bot is a little bit tricky. It  
# has to be configured for you discord room. 
# https://discordpy.readthedocs.io/en/stable/discord.html#discord-intro

import os
import pandas as pd
import discord

# Reads your secret token from .env file
TOKEN = os.getenv('DISCORD_TOKEN')

category_list = []
textchannel_list = []
textmessage_list = []

client = discord.Client()
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    # Step 1: Crawling all channels and determine their types. The discord
    # API has different namings for individual object types
    print("Crawling all channels ... ", end="")
    channels = client.get_all_channels()
    for channel in channels:
        if isinstance(channel, discord.channel.CategoryChannel):
            category_entry = {
                "category_id": channel.id,
                "category_name": channel.name,
            }
            category_list.append(category_entry)

        if isinstance(channel, discord.channel.TextChannel):
            textchannel_entry = {
                "category_id": channel.category_id,
                "textchannel_id": channel.id,
                "channel_obj": channel,
                "textchannel_name": channel.name,
            }
            textchannel_list.append(textchannel_entry)
    print(f"found {len(textchannel_list)} text channels in {len(category_list)} categories!")

    # Step 2: Extracting text messages in all categories
    print(category_list)
    print("Extracting all messages ...")
    for textchannel in textchannel_list:
        print("   " + textchannel["textchannel_name"] + " ... ", end="")
        try:
            messages = await textchannel["channel_obj"].history(limit=1000).flatten()
        except:
            pass
        count = 0
        for message in messages:
            count=count+1
            message_entry = {
                "textchannel_id": textchannel["channel_obj"].id,
                "message_id": message.id,
                "content": message.content,
                "created_at": message.created_at,
                "author_id": message.author.id,
            }
            textmessage_list.append(message_entry)
        print(f"{count} messages found")

    print(f"{len(textmessage_list)} messages at all.")

    df_textmessage_list = pd.DataFrame(textmessage_list)
    df_textmessage_list.to_pickle("./textmessage_list.p")

    df_textchannel_list = pd.DataFrame(textchannel_list)
    df_textchannel_list.drop("channel_obj", axis = 1, inplace=True)
    df_textchannel_list.to_pickle("./textchannel_list.p")

    df_category_list = pd.DataFrame(category_list)
    df_category_list.to_pickle("./category_list.p")

    print("Aus die Maus")

client.run(TOKEN)
