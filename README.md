# 🛰️ Soracord

A lightweight Discord bot designed for **VPS health monitoring** and **Docker container management**. Get real-time metrics, logs, and status updates directly from your Discord server.

## 🚀 Getting Started

### 1. Create a Discord Bot Token

To interact with the Discord API, you need a bot account:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** and give it a name (e.g., `Soracord`).
3. Navigate to the **Bot** tab on the left sidebar.
4. **Crucial:** Scroll down to **Privileged Gateway Intents** and enable **Message Content Intent**.
5. Click **Reset Token** (or **Copy**) to get your `BOT_TOKEN`. Keep this secret!
6. Use the **OAuth2 > URL Generator** to invite the bot to your server with `bot` and `Administrator` permissions.

### 2. Configure Environment

Clone this repository and set up your secrets:

```bash
# Move the example env file
mv .env.example .env

# Edit the file and paste your token
```

```

### 3. Prerequisites

Ensure you have **Docker** and **Docker Compose** installed on your VPS.

* [Official Docker Installation Guide](https://docs.docker.com/engine/install/)

---

## 🛠️ Installation & Deployment

Soracord is fully containerized. It automatically mounts your host's Docker socket to monitor sibling containers.

**Run the stack:**

```bash
docker compose up -d --build

```

---

## 🎮 Commands

The default prefix is `!`.

| Command | Description |
| --- | --- |
| `!soracord health` | Shows VPS CPU usage, RAM, and Disk space with visual progress bars. |
| `!soracord docker` | Lists all containers, their current status, and healthcheck results. |
| `!soracord logs [name]` | Fetches the last 10-15 lines of logs for a specific container. |
| `!soracord container [name]` | Displays detailed live metrics (CPU%, RAM%, Net IO, Disk IO) for a container. |

---

## 📝 Configuration Note

To see "Healthy" or "Unhealthy" statuses in the `!soracord docker` command, ensure your other containers have a `healthcheck` defined in their `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 1m
  timeout: 10s
  retries: 3

```


