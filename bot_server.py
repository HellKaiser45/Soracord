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


@bot.command()
async def health(ctx):
    cpu_usage = cpu()
    disk_usage = disk()
    ram_usage = ram()

    embed = discord.Embed(
        title="🖥️ Server Health",
        description="Current VPS metrics",
        color=discord.Color.green()
        if cpu_usage.usage_percent < 80
        else discord.Color.red(),
        timestamp=discord.utils.utcnow(),
    )

    embed.add_field(
        name="💻 CPU Usage", value=f"`{cpu_usage.usage_percent:.1f}%`", inline=True
    )

    embed.add_field(
        name="🧠 RAM",
        value=f"`{ram_usage.used:.1f}` / `{ram_usage.total:.1f}` GB",
        inline=True,
    )

    embed.add_field(
        name="💾 Disk",
        value=f"`{disk_usage.used:.1f}` / `{disk_usage.total:.1f}` GB",
        inline=True,
    )

    embed.set_footer(text="Last updated")

    await ctx.send(embed=embed)


# 3. Run the bot
bot.run(Discord_Token)
