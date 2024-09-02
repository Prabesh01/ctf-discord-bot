
import os
from pathlib import Path
from dotenv import load_dotenv

import discord
from discord.ext.commands import Bot
from discord import app_commands

import requests

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'
load_dotenv(ENV_FILE)
API_KEY=os.environ.get('API_KEY')

intents = discord.Intents.default()
bot = Bot(command_prefix='/', intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready() -> None:
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.tree.sync()


@bot.tree.command(name="flag", description="Submit CTF Flag")
@app_commands.describe(challenge="name of the challenge", flag="flag to submit")
async def flag(interaction: discord.Interaction, flag: str, challenge: str =None):
    rr=requests.post(os.environ.get('django_web_url')+'/api/submit_flag/', data={'user':interaction.user.id,"challenge":challenge, "flag": flag}, headers={"X-API-Key":API_KEY})
    try:
        await interaction.response.send_message(rr.text, ephemeral=True)
    except:
        await interaction.response.send_message(f"Sth went wrong. Please try again later!", ephemeral=True)    

bot.run(os.environ.get("bot_token"))