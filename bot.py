import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import io
import os
import re
from dotenv import load_dotenv

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
                    await download_and_send_gif(message, message.content)
                    
        except discord.NotFound:
            pass
        except Exception as e:
            print(f"Error checking reply: {e}")

async def download_and_send_gif(ctx_message, text):
    url_match = re.search(r"(https?://tenor\.com/view/[a-zA-Z0-9-]+)", text)
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



bot.run(token)
