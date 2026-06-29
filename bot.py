import random

import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import io
import os
import re
from dotenv import load_dotenv
import json
import asyncio

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
mod_id = int(os.getenv("MOD"))
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@tree.command(name="say")
async def say(interaction: discord.Interaction, message: str):

    if interaction.user.id == mod_id:
        await interaction.response.send_message("Message sent :3", ephemeral=True)
        await interaction.channel.send(message)
    else:
        await interaction.response.send_message("Can't talk as me!", ephemeral=True)

@tree.command(name="help")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(f"**Available Commands:**\n"
                                            f"- `/help` - Show this help message\n"
                                            f"- `/download_from_json` - Download GIFs from a JSON file\n\n"
                                            f"You can save Tenor gifs by replying to *any* message from Toast.\n\n"
                                            f"To get a JSON file to use with the /download_from_json command, you can use the script in following link with the **Vencord** developer console: https://raw.githubusercontent.com/Chalksies/toast/refs/heads/main/script)\n"
                                            f"You can then directly attach the file when using the command. Toast will automatically download and send the gifs on the list (if it's on Tenor) to the channel it was ran in.")

@tree.command(name="download_from_json")
async def download_from_json(interaction: discord.Interaction, file: discord.Attachment):
    if not file.filename.endswith('.json'):
        await interaction.response.send_message("Please upload a valid `.json` file!!", ephemeral=True)
        return 
    
    await interaction.response.defer(thinking=True, ephemeral=False)

    try:
        file_bytes = await file.read()
        urls = json.loads(file_bytes.decode('utf-8'))
            
        if not isinstance(urls, list):
            await interaction.followup.send("Invalid format :c The JSON should be a list of URLs.")
            return

        total_gifs = len(urls)
        await interaction.followup.send(f"Found {total_gifs} GIFs. Starting the archival process...")

        for url in urls:
            await download_and_send_auto(interaction, url)
            pass

        await interaction.followup.send("Bulk archival complete!!! :3")

    except json.JSONDecodeError:
        await interaction.followup.send("Failed to parse JSON. Check if the file is corrupted.")
    except Exception as e:
        await interaction.followup.send(f"An error occurred while processing the file: {e}")
        
        
        
@bot.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.reference:
        try:
            original_message = message.reference.resolved
            if original_message is None:
                original_message = await message.channel.fetch_message(message.reference.message_id)

            if original_message.author == bot.user:
                if "tenor.com/view" in message.content:
                    print("Tenor link detected! Further validating URL...")
                    await download_and_send_manual(message, message.content)
                    
        except discord.NotFound:
            pass
        except Exception as e:
            print(f"Error checking reply: {e}")

async def download_and_send_manual(ctx_message, text):
    url_match = re.search(r"(https?://tenor\.com/view/[%a-zA-Z0-9-]+)", text)
    if not url_match:
        print("No regex match... Skipping this message!")
        return
    
    print("Regex matched! Proceeding :fluffycar:")
    url = url_match.group(1)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'} 
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print("Parsing webpage!")
        meta_tag = soup.find("meta", property="og:image")
        
        if not meta_tag:
            await ctx_message.reply("Could not extract GIF data...")
            return
            
        gif_url = meta_tag["content"]
        
        gif_data = requests.get(gif_url)
        gif_data.raise_for_status()

        file_obj = io.BytesIO(gif_data.content)
        file_obj.seek(0)

        filename = f"archived_{url.split('/')[-1]}.gif"
        print("Sending gif!")
        await ctx_message.reply(file=discord.File(fp=file_obj, filename=filename))

    except Exception as e:
        await ctx_message.reply(f"Failed to download or send the gif: {e}")

async def download_and_send_auto(interaction, link):
    url_match = re.search(r"(https?://tenor\.com/view/[%a-zA-Z0-9-]+)", link)
    if not url_match:
        print("No regex match... Skipping this link!")
        return
    
    await asyncio.sleep(random.uniform(0.5, 1.5)) 
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'} 
        response = requests.get(link, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print("Parsing webpage!")
        meta_tag = soup.find("meta", property="og:image")
        
        if not meta_tag:
            print("Could not extract GIF data...")
            return
            
        gif_url = meta_tag["content"]
        
        gif_data = requests.get(gif_url)
        gif_data.raise_for_status()

        file_obj = io.BytesIO(gif_data.content)
        file_obj.seek(0)

        filename = f"archived_{link.split('/')[-1]}.gif"
        print("Sending gif!")
        await interaction.channel.send(file=discord.File(fp=file_obj, filename=filename))

    except Exception as e:
        print(f"Failed to download or send the gif: {e}")


bot.run(token)
