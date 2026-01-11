# This example requires the 'message_content' intent.

import discord
from discord.ext import commands
from dotenv import load_dotenv
from health import cpu, ram, disk
import os

load_dotenv()
Discord_Token = os.getenv("BOT_TOKEN")


# 1. Setup Intents (You already did this, which is great!)
intents = discord.Intents.default()
intents.message_content = True

# 2. Define the bot with a prefix (e.g., '!')
bot = commands.Bot(command_prefix="!", intents=intents)


# This event runs when the bot starts
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    print("Ready for commands...")


# --- BASIC COMMANDS ---


# A simple text command. Usage: !ping
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {disk()}")


# A command with an argument. Usage: !echo Hello World
@bot.command()
async def echo(ctx, *, message):
    await ctx.send(message)


# 3. Run the bot
bot.run(Discord_Token)
