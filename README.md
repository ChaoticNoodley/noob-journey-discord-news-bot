# Discord News Bot

**A Curious Beginner’s Journey Building a Discord News Bot**

This project is a simple Discord bot made with Python that automatically fetches and posts news about Windows and Linux systems into a Discord server **using RSS feeds**.  
It was created mainly for learning purposes and just for fun.

I'm still a beginner in programming, so this project represents my experiments, mistakes, and learning process.

---

## 🚀 Features

- **RSS Based:** Fetches news directly from RSS feeds of your favorite tech sites.
- **Fully Customizable:** The list of news sources is open to modification—you can easily add or remove any RSS feed.
- **Automated Updates:** Sends messages to a Discord channel automatically.
- **Focused Content:** Primarily configured for Windows and Linux news.
- **Simple and lightweight:** Beginner-friendly code.

---

## 🛠 Technologies

- Python 3
- [discord.py](https://github.com/Rapptz/discord.py)
- [feedparser](https://github.com/kurtmckee/feedparser) (for handling RSS feeds)
- JSON file for tracking sent news

---

## 📁 Project Structure

noticias_bot/
│
├── bot.py                # Main bot logic
├── news_fetcher.py       # RSS fetching and parsing
├── sent_news.json        # Database to avoid duplicate posts
├── env.example           # Template for environment variables
├── README.md
└── .gitignore

---

## Setup

1. Clone the repository:
```bash
git clone https://github.com/ChaoticNoodleyYokaii/noob-journey-discord-news-bot.git
```

2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a .env file based on env.example and add your Discord bot token
(Optional) Modify news_fetcher.py to add your preferred RSS feed URLs.

5. Run the bot
```bash
python bot.py
```

---

### Notes
- This project is for learning and personal use.

- Contributions and suggestions are welcome.

- Do not forget to keep your Discord token private.

---

### Motivation
This bot was created as a personal challenge to learn more about:

- Python

- APIs

- Discord bots

- Automation

---

## 📜 License

Free to use for learning and personal projects.
