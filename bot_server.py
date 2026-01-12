import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Your custom imports
from health import cpu, ram, disk
from docker_client import DockerMonitor

load_dotenv()
Discord_Token = os.getenv("BOT_TOKEN")

# Persistent instance: Connect once, use everywhere
monitor = DockerMonitor()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!soracord ", intents=intents, help_command=None)

# --- HELPERS ---


def get_status_emoji(status: str, health: str) -> str:
    """Returns a visual indicator based on container state."""
    if health == "healthy":
        return "🟢"
    if health == "unhealthy":
        return "🔴"
    if status == "running":
        return "🔵"
    if status == "exited":
        return "⚪"
    return "🟡"


def create_progress_bar(percent: float) -> str:
    """Creates a simple text-based progress bar."""
    filled = int(percent / 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"`{bar}` {percent:.1f}%"


# --- COMMANDS ---


@bot.event
async def on_ready():
    print(f"🚀 {bot.user} is online and monitoring Docker.")


@bot.command()
async def health(ctx):
    """General VPS health overview."""
    c, r, d = cpu(), ram(), disk()

    embed = discord.Embed(
        title="🖥️ Server Health Report",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow(),
    )

    embed.add_field(
        name="CPU Load", value=create_progress_bar(c.usage_percent), inline=False
    )
    embed.add_field(
        name="RAM Usage", value=f"💾 `{r.used:.1f} / {r.total:.1f} GB`", inline=True
    )
    embed.add_field(
        name="Disk Space", value=f"📂 `{d.used:.1f} / {d.total:.1f} GB`", inline=True
    )
    embed.set_footer(text="System Monitoring")

    await ctx.send(embed=embed)


@bot.command()
async def docker(ctx):
    """List all containers with status emojis."""
    containers = (
        monitor.check_containers()
    )  # Assuming this returns a list of dataclasses

    embed = discord.Embed(
        title="🐳 Docker Infrastructure",
        description=f"Monitoring **{len(containers)}** containers.",
        color=discord.Color.dark_grey(),
    )

    status_list = []
    for c in containers:
        emoji = get_status_emoji(c.status, c.health)
        status_list.append(f"{emoji} **{c.name}** \u2014 `{c.status}`")

    embed.description = "\n".join(status_list)
    await ctx.send(embed=embed)


@bot.command()
async def container(ctx, name: str):
    """Detailed metrics for a specific container."""
    stats = monitor.get_metrics(name)

    if not stats:
        return await ctx.send(f"❌ Container `{name}` not found.")

    embed = discord.Embed(title=f"📦 Details: {name}", color=discord.Color.blue())

    # Grid Layout
    embed.add_field(name="CPU Usage", value=f"`{stats.cpu_pct}%`", inline=True)
    embed.add_field(
        name="Memory", value=f"`{stats.mem_mb}MB` ({stats.mem_pct}%)", inline=True
    )
    embed.add_field(
        name="Network IO",
        value=f"⬇️ `{stats.io.net_rx_gb}GB` | ⬆️ `{stats.io.net_tx_gb}GB`",
        inline=False,
    )
    embed.add_field(
        name="Disk IO",
        value=f"📖 `{stats.io.disk_read_mb}MB` | ✍️ `{stats.io.disk_write_mb}MB`",
        inline=False,
    )

    await ctx.send(embed=embed)


@bot.command()
async def logs(ctx, name: str, lines: int = 15):
    """Fetch recent logs in a clean code block."""
    raw_logs = monitor.container_logs(name, lines=lines)

    if not raw_logs:
        return await ctx.send("No logs found.")

    # Truncate if logs are too long for Discord (2000 char limit)
    if len(raw_logs) > 1900:
        raw_logs = raw_logs[-1900:]

    await ctx.send(f"📋 **Last {lines} lines for `{name}`:**\n```text\n{raw_logs}\n```")


bot.run(Discord_Token)
