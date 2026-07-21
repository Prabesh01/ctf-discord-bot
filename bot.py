from datetime import datetime
import csv

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

from discord import Spotify
intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = Bot(command_prefix='/', intents=intents)
bot.remove_command('help')

@bot.event
async def on_presence_update(before, after):
    if after.bot: return

    if str(after.status) in ["invisible" ,"offline"]: status = 0
    else: status = 1

    if str(before.status) in ["invisible" ,"offline"]: last_status = 0
    else: last_status = 1

    was = False
    if before.activities:
        for activity in before.activities:
            if isinstance(activity, Spotify): was = activity

    found = False
    if after.activities:
        for activity in after.activities:
            if isinstance(activity, Spotify):
                found=activity
                break

    seek=None
    if found and was:
        if was.track_id==found.track_id:
            seek=1
            # seek=int((was.start - found.start).total_seconds()*1000)
            # requests.get(f"{os.environ.get('ARK_FM_SITE_URL')}/activity_seek?&uid={after.id}&seek={seek}")

    if found and not seek:
        # print(f"{found.name} is now listening to {found.title} by {found.artist}")
        r=requests.get(f"{os.environ.get('ARK_FM_SITE_URL')}/activity?track={found.track_id}&uid={after.id}&user={after.global_name}&profile={after.avatar}&title={found.title}&artist={found.artist}&cover={found.album_cover_url}&start={found.start}")

    if was and not found:
        requests.get(f"{os.environ.get('ARK_FM_SITE_URL')}/activity_rm?uid={after.id}")

    # print(f"{str(after)}: {before.status} -> {after.status}")


@bot.event
async def on_ready() -> None:
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.tree.sync()


@bot.tree.command(name="flag", description="Submit CTF Flag")
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=False)
@app_commands.describe(challenge="name of the challenge", flag="flag to submit")
async def flag(interaction: discord.Interaction, flag: str, challenge: str =None):
    guild=interaction.guild
    if not guild: return
    rr=requests.post(os.environ.get('django_web_url')+'/api/submit_flag/', data={'user':interaction.user.id,"challenge":challenge, "flag": flag,"server":guild.id}, headers={"X-API-Key":API_KEY})
    try:
        await interaction.response.send_message(rr.text, ephemeral=True)
    except:
        await interaction.response.send_message(f"Sth went wrong. Please try again later!", ephemeral=True)    

bot.run(os.environ.get("bot_token"))
