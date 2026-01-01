<div align="center">
    <img src="https://github.com/AndriiBash/tetOS/blob/main/.github/images/mainIcon.png" alt="screenshot tetOS)">

## TetOS — manage your Minecraft server with ease!

</div>

<div align="center">

  ![Python](https://img.shields.io/badge/Python_Version-3.9.6-yellow?logo=python)
  ![Python](https://img.shields.io/badge/Telebot--4.29.1-3776AB?&logo=telegram&logoColor=white)
</div>

<p align="center">
    <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/AndriiBash/tetOS/blob/main/.github/images/terminalView~dark.png">
    <img src="https://github.com/AndriiBash/tetOS/blob/main/.github/images/terminalView.png" alt="screenshot tetOS)">
    </picture>
</p>

**TetOS** is a CLI utility for managing a local Minecraft server. It allows you to get the server status (RAM usage, world weight, count of players, etc.). If desired, send notifications to Telegram via a bot about events on the server, such as players logging in and out or server readiness. The official core of the Minecraft Java server is used for work.

Libraries used for tetOS:
- `psutil` - to control the use of server resources (RAM).  
- `python-telebot` - for sending notifications to Telegram about events on the server.  
- `python-dotenv` - configuration of the secure storage component (.env file).

<div align="center">

## Telegram Bot

</div>

<p align="center">
    <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/AndriiBash/tetOS/blob/main/.github/images/telegramView~dark.png">
    <img src="https://github.com/AndriiBash/tetOS/blob/main/.github/images/telegramView.png" alt="screenshot tetOS) telegram">
    </picture>
</p>

How it is worked? The Telegram bot in tetOS is used only for notifications and basic interaction with the server. TetOS controls the Minecraft server (logs, status, events). When an event occurs (server start/stop, player joining/leaving), tetOS sends a message to the Telegram bot. Telegram bot delivers notifications to all registered users.

Scheme Telegram-bot workflow
```
User (Telegram)
      │
      ▼
Telegram Bot
      │
      ▼
tetOS (CLI utility)
 ├── .env           (bot token)
 ├── tg_users.txt   (subscribed users)
      │
      ▼
Minecraft Java Server
```

<div align="center">

## Supported Operating Systems

| **OS** | **Build** | **Notes** |
|:---:|:---:| :---: |
| **MacOS** | ✅ Full | Tested on OSX Tahoe
| **Linux** | ⚠️ Partially | Bash script available
| **Windows** | ❌ WIP | Support coming soon

</div>

<div align="center">

## Basic commands

</div>

An important point for the utility is the commands, the main commands will look like this
```
info - Show server status (RAM, players, version, etc.)
start - Start the server (optional: --hard for hard start)
stop - Stop the server
restart - Restart the server
clear/cls - Clear the terminal
tps - Show server TPS
mspt - Show MSPT servers
exit - Exit the utility
```

<div align="center">

## File System Structure

</div>

The file system structure of the utility will look like this

```
tetOS/
├── README.md                 # Project documentation
├── python_scripts/           # Dir with python utility scripts
│   ├── config.py             # Configs and global variables
│   ├── main.py               # Main CLI script
│   ├── server_commands.py    # Server control logic
│   ├── telegram_bot.py       # Telegram bot logic
│   └── .env                  # Environment variables (telegram bot token)
├── run_server.sh             # Minecraft server startup script
├── run.sh                    # tetOS utility launch script
├── telegram_cache/           # Telegram dir
│   └── tg_users.txt          # Telegram user cache
├── world                     # Minecraft world dir
├── requirements.txt          # Python requirements for running TetOS 
└── server.properties         # Minecraft server configuration (port, max-players, etc.)
```

<div align="center">

## Getting Started
</div>

### 1. Installation tetOS


Clone the repository:
```bash
git clone https://github.com/AndriiBash/tetOS.git
cd tetOS
```

### 2. Install Python dependencies

Install dependencies using pip:
```bash
pip install -r requirements.txt
```

### 3. Install Minecraft Java server
Download the official Minecraft Java server from the official site. 
[Download Server](https://www.minecraft.net/en-us/download/server).


### 4. Configure server

1. Move the downloaded server file (e.g.,`server.jar`) into the folder where `tetOS` is located.  

2. Execute `server.jar`:  

```bash
java -jar server.jar
```

3. After this, you need to accept the license agreement to start the server. Go to the `eula.txt` file and change `eula=false` to `eula=true`. Use this command to do so:

**MacOS/Linux:**
```bash
sed -i.bak 's/eula=false/eula=true/' eula.txt && rm eula.txt.bak
```
**Windows:**
```bash
Null
```

### 5. Run TetOS
Start the utility using.

**MacOS/Linux:**
```bash
cd tetOS
./run.sh
```
*Make sure run.sh is executable:*
```bash
chmod +x run.sh
```

**Windows:**
```bash
Null
```
