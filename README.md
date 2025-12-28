main_icon

# tetOS
## Welcome to tetOS

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=yellow)

**tetOS** is a CLI utility for managing a local Minecraft server. It allows you to get the server status (RAM usage, world weight, count of players, etc.). If desired, send notifications to Telegram via a bot about events on the server, such as players logging in and out or server readiness. The official core of the Minecraft Java server is used for work.

Libraries used for tetOS:
- **psutil** - to control the use of server resources (RAM).  
- **python-telebot** - for sending notifications to Telegram about events on the server.  
- **python-dotenv** - configuration of the secure storage component (.env file).

### Supported Operating Systems
| **OS** | **Build** | **Notes** |
|:---:|:---:| :---: |
| **MacOS** | ✅ Full | Tested on OSX Tahoe
| **Linux** | ⚠️ Partially | Bash script available
| **Windows** | ❌ WIP | Support coming soon






### Basic commands
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

### File System Structure

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
└── server.properties         # Minecraft server configuration (port, max-players, etc.)
```

## Getting Started
### Installation tetOS

Clone the repository:
```bash
git clone https://github.com/AndriiBash/tetOS.git
cd tetOS
```

### Install Python dependencies

!!no_text!!

### Install Minecraft Java server
Download the official Minecraft Java server from the official site. 
[Download Server](https://www.minecraft.net/en-us/download/server).


### Configure server

!!no_text!!


### Run TetOS
Start the utility using.

MacOS:
```
cd tetOS
./run.sh
```

Linux:
```
cd tetOS
bash run.sh
```

Windows:
```
Null
```
