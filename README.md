# Winux-chan — Discord News Bot

**A Curious Beginner’s Journey Building a Discord News Bot**

Winux-chan is a Discord bot written in Python that automatically posts news about Windows and Linux using RSS feeds from reliable tech websites.

The bot is now configurable per server via commands, so no code editing is required to set it up.
---

## Features

- Automatic news about Windows and Linux
- Server-based configuration (multi-server support)
- Configurable news channel via command
- Fixed check interval (e.g., every 1 hour)
- Multiple RSS sources
- Fault-tolerant (does not crash if a feed is offline)
- Saves already sent news to avoid reposting

---

## Technologies

- Python 3
- [discord.py](https://github.com/Rapptz/discord.py)
- [feedparser](https://github.com/kurtmckee/feedparser) (for handling RSS feeds)
- JSON file for tracking sent news
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## Project Structure

noticias_bot/
│
├── bot.py
├── news_fetcher.py
├── server_config.json
├── sent_news.json
├── .env
└── venv/

---

## Setup

### Windows

1. Install Python 3.10+ from:
https://www.python.org/downloads/windows/

(Check **"Add Python to PATH"** during installation)

2. Clone the repository:
```bash
git clone https://github.com/yourusername/yourrepository.git
cd yourrepository
```
3. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```
5. Create the .env file:
```bash
DISCORD_TOKEN:
ROLE_LINUX_ID:
ROLE_WINDOWS_ID:
OPENAI_API_KEY= *Fill it in if you want, just remember to update the code*
CHECK_INTERVAL=3600
```
6. Create the configuration file:
```bash
echo {} > server_config.json
```
7. Run the bot:
```bash
python bot.py
```

### Linux/MacOS

1. Install Python 3.10+:
```bash
sudo apt install python3 python3-venv python3-pip   # Ubuntu/Debian
brew install python                                 # macOS (Homebrew)
```
2. Clone the repository
```bash
git clone https://github.com/yourusername/yourrepository.git
cd yourrepository
```
3. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```
5. Create the .env file:
```bash
DISCORD_TOKEN:
ROLE_LINUX_ID:
ROLE_WINDOWS_ID:
OPENAI_API_KEY= *Fill it in if you want, just remember to update the code*
CHECK_INTERVAL=3600
```
6. Create the configuration file:
```bash
echo "{}" > server_config.json
```
7. Run the BOT
```bash
python3 bot.py
```
---
## Commands

### Set the news channel
- Run this command in the desired channel:
 !setchannel
 !testnews

---

## Notes
- This project is for learning and personal use.

- Customization: You can change the news sources by editing the RSS URL list in the code.

- Contributions and suggestions are welcome.

- Do not forget to keep your Discord token private.
  
---

## Motivation
This bot was created as a personal challenge to learn more about:

- Python

- RSS Feeds & Data Parsing

- Discord bots

- Automation

---

## 📜 License

Free to use for learning and personal projects.
