
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'
load_dotenv(ENV_FILE)
COMM_FILE_PATH = BASE_DIR / os.environ.get('COMM_FILE')
API_KEY=os.environ.get('API_KEY')

import discord
from discord.ext import tasks
from discord.ext.commands import Bot, Context
from discord import app_commands

intents = discord.Intents.default()
bot = Bot(command_prefix='/', intents=intents)
bot.remove_command('help')

import requests
import json
from difflib import get_close_matches

challenges={}
async def fetch_challenges_api():
    global challenges
    rr=requests.get(os.environ.get('django_web_url')+'/api/get_challenges/', headers={"X-API-Key":API_KEY})
    try:
        for i in rr.json()['challenges']:
            challenges[i['title']]=[i['id'],i['flag']]
    except:
        print("json_decode_err: "+rr.text)

async def fetch_challenges_file():   
    try:     
        global challenges
        json_data = json.load(open(COMM_FILE_PATH,'r'))
        for i in json_data['challenges']:
            challenges[i['title']]=[i['id'],i['flag']]
        os.remove(COMM_FILE_PATH)
    except:
        print("json_decode_err: "+open(COMM_FILE_PATH,'r').read())

@tasks.loop(minutes=0.1)
async def update_challenges():
    try:
        if os.path.exists(COMM_FILE_PATH):
            await fetch_challenges_file()
    except:
        print("update_challenge_task_error")

@bot.event
async def on_ready() -> None:
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await fetch_challenges_api()
    update_challenges.start()
    await bot.tree.sync()


@bot.tree.command(name="flag", description="Submit CTF Flag")
@app_commands.describe(challenge="name of the challenge", flag="flag to submit")
async def flag(interaction: discord.Interaction, flag: str, challenge: str =None):
    if not challenge:
        challenge=list(challenges.keys())[0]
    else:
        challenge = get_close_matches(challenge, challenges.keys())
        if challenge: challenge = challenge[0]
    if not challenge:
        await interaction.response.send_message("Challenge not found", ephemeral=True)
        return
    challenge_id=challenges[challenge][0]
    flag_=challenges[challenge][1]
    if flag_==flag:
        rr=requests.post(os.environ.get('django_web_url')+'/api/submit_flag/', data={'user':interaction.user.id,"challenge":challenge_id}, headers={"X-API-Key":API_KEY})
        if rr.status_code==200:
            await interaction.response.send_message(f"Correct! - {challenge}", ephemeral=True)
        elif rr.status_code==202:
            await interaction.response.send_message(f"Correct! I said the same last time - {challenge}", ephemeral=True)
        else:
            await interaction.response.send_message(f"Sth went wrong. Please try again later! - {challenge}", ephemeral=True)    
    else:
        await interaction.response.send_message(f"Wrong Flag - {challenge}", ephemeral=True)

bot.run(os.environ.get("bot_token"))