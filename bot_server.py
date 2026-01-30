import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from dataclasses import dataclass
from health import cpu, ram, disk
from docker_client import DockerMonitor

load_dotenv()
Discord_Token = os.getenv("BOT_TOKEN")
Server_Name = os.getenv("SERVER_NAME") or "My server"

monitor = DockerMonitor()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!soracord ", intents=intents)


# --- Structure ---
@dataclass
class Alert:
    channel_id: int = int(os.getenv("CHANNEL_ID") or 0)

    async def send_alert(self, embed: discord.Embed):
        channel = bot.get_channel(self.channel_id)
        await channel.send(embed=embed)

    async def monitor(self, monitor: DockerMonitor = DockerMonitor()):
        print("boucle de monitoring")
        containers = monitor.check_containers()
        for container in containers:
            if container.health == "unhealthy" or container.status == (
                "dead" or "restarting"
            ):
                embed = discord.Embed(
                    title=f"{Server_Name}: Unhealthy",
                    description=f"Container `{container.name}` is unhealthy.",
                    color=discord.Color.red(),
                )
                stats = monitor.get_metrics(container.name)
                embed.add_field(
                    name="CPU Usage", value=f"`{stats.cpu_pct}%`", inline=True
                )
                embed.add_field(
                    name="Memory",
                    value=f"`{stats.mem_mb}MB` ({stats.mem_pct}%)",
                    inline=True,
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

                raw_logs = monitor.container_logs(container.name)

                if not raw_logs:
                    raw_logs = "No logs found."

                elif len(raw_logs) > 512:
                    raw_logs = raw_logs[-512:]

                embed.add_field(
                    name="Logs", value=f"```\n{raw_logs}\n```", inline=False
                )
                await self.send_alert(embed)


async def monitoring_loop(AlertManager: Alert = Alert(), check_frequency: int = 3600):
    await bot.wait_until_ready()
    while not bot.is_closed():
        await AlertManager.monitor()
        await asyncio.sleep(check_frequency)


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
    bot.loop.create_task(monitoring_loop())


@bot.command()
async def health(
    ctx,
    server: str | None = commands.parameter(
        default=None, description=": The name of the server to check health"
    ),
):
    """General VPS health overview."""

    c, r, d = cpu(), ram(), disk()

    embed = discord.Embed(
        title=f"🖥️ Server {Server_Name}: Health Report",
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
    if not server or server == Server_Name:
        await ctx.send(embed=embed)
    else:
        pass


@bot.command()
async def docker(
    ctx,
    server: str | None = commands.parameter(
        default=None, description=": The name of the server to check health"
    ),
):
    """List all containers with status emojis."""
    containers = (
        monitor.check_containers()
    )  # Assuming this returns a list of dataclasses

    embed = discord.Embed(
        title=f"🐳 Docker {Server_Name} Infrastructure",
        description=f"Monitoring **{len(containers)}** containers.",
        color=discord.Color.dark_grey(),
    )

    status_list = []
    for c in containers:
        emoji = get_status_emoji(c.status, c.health)
        status_list.append(f"{emoji} **{c.name}** \u2014 `{c.status}`")

    embed.description = "\n".join(status_list)

    if not server or server == Server_Name:
        await ctx.send(embed=embed)
    else:
        pass


@bot.command()
async def container(
    ctx,
    name: str = commands.parameter(description=": The name of the container"),
    server: str | None = commands.parameter(
        default=None, description=": The name of the server to check health"
    ),
):
    """Detailed metrics for a specific container."""
    stats = monitor.get_metrics(name)

    if not stats:
        return

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

    if not server or server == Server_Name:
        await ctx.send(embed=embed)
    else:
        pass


@bot.command()
async def logs(
    ctx,
    name: str = commands.parameter(description=": The name of the container"),
    lines: int = commands.parameter(
        default=15, description=": The number of lines of logs to retreive"
    ),
    server: str | None = commands.parameter(
        default=None, description=": The name of the server to check health"
    ),
):
    """Fetch recent logs in a clean code block."""
    raw_logs = monitor.container_logs(name, lines=lines)

    if not raw_logs:
        return

    if len(raw_logs) > 1900:
        raw_logs = raw_logs[-1900:]
    if not server or server == Server_Name:
        await ctx.send(
            f"📋 **Last {lines} lines for `{name}`:**\n```text\n{raw_logs}\n```"
        )
    else:
        pass


bot.run(Discord_Token)
