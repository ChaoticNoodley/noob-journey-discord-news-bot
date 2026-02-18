# Winux-chan: Discord News Bot

![GitHub repo size](https://img.shields.io/github/repo-size/ChaoticNoodley/noob-journey-discord-news-bot?style=for-the-badge)
![GitHub language count](https://img.shields.io/github/languages/count/ChaoticNoodley/noob-journey-discord-news-bot?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/ChaoticNoodley/noob-journey-discord-news-bot?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/ChaoticNoodley/noob-journey-discord-news-bot?style=for-the-badge)

<img src="https://imgur.com/eQq2K8i.png" alt="Winux-chan Bot">

> **PT-BR:**  
> Winux-chan é um bot de Discord escrito em Python que publica automaticamente notícias sobre Windows e Linux usando feeds RSS de sites confiáveis de tecnologia.  
> O bot é configurável por servidor e não exige edição de código para funcionar.

> **EN:**  
> Winux-chan is a Discord bot written in Python that automatically posts Windows and Linux news using RSS feeds from reliable tech websites.  
> The bot is configurable per server and requires no code editing to run.

---

## ⚙️ Ajustes e melhorias | Improvements

O projeto ainda está em desenvolvimento e as próximas atualizações incluem:  
The project is still under development and upcoming updates include:

- [x] Sistema automático de RSS | Automatic RSS system  
- [x] Suporte a múltiplos servidores | Multi-server support  
- [x] Canal configurável por comando | Configurable channel via command  
- [x] Evita repostar notícias | Prevents duplicate news  
- [ ] Mais fontes de notícias | More news sources  
- [ ] Sistema de categorias (Windows / Linux) | Category system (Windows / Linux)  
- [ ] Melhor sistema de configuração | Improved configuration system  

---

## 💻 Pré-requisitos | Requirements

Antes de começar, você precisa:  
Before you begin, make sure you have:

- Python **3.10+**
- Sistema operacional | Operating System:
  - ✅ Windows  
  - ✅ Linux  
  - ✅ macOS
- Conhecimento básico de:
  - Discord bots
  - Terminal / Command line

---

## 🚀 Instalando Winux-chan | Installing Winux-chan

### Linux e macOS

```bash
git clone https://github.com/ChaoticNoodley/noob-journey-discord-news-bot.git
cd noob-journey-discord-news-bot

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Crie o arquivo .env:
Create the .env file:
```env
DISCORD_TOKEN=
ROLE_LINUX_ID=
ROLE_WINDOWS_ID=
OPENAI_API_KEY=
CHECK_INTERVAL=3600
```

Crie o arquivo de configuração:
Create the config file:
```bash
echo "{}" > server_config.json
```

Execute o bot:
Run the bot:
```bash
python3 bot.py
```

### Windows
```bash
git clone https://github.com/ChaoticNoodley/noob-journey-discord-news-bot.git
cd noob-journey-discord-news-bot

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

Crie o arquivo .env:
Create the .env file:
```bash
DISCORD_TOKEN=
ROLE_LINUX_ID=
ROLE_WINDOWS_ID=
OPENAI_API_KEY=
CHECK_INTERVAL=3600
```

Crie o arquivo de configuração:
Create the config file:
```bash
echo {} > server_config.json
```

Execute o bot:
Run the bot:
```bash
python bot.py
```

## ☕ Usando Winux-chan | Using Winux-chan

Após iniciar o bot no seu servidor Discord, utilize os comandos:
After starting the bot on your Discord server, use the commands:

```bash
!setchannel
!testnews
```
Exemplo | Example:
- Vá até o canal desejado | Go to the desired channel
- Execute !setchannel
- O bot enviará notícias automaticamente | The bot will start posting news automatically

## 📂 Estrutura do projeto | Project Structure
```sql
noticias_bot/
│
├── bot.py
├── news_fetcher.py
├── server_config.json
├── sent_news.json
├── .env
└── venv
```
## 🤝 Colaborador | Contributor
<table> <tr> <td align="center"> <a href="https://github.com/ChaoticNoodley"> <img src="https://github.com/ChaoticNoodley.png" width="100px;" alt="Foto do autor"/><br> <sub> <b>Bruno Ceroni</b> </sub> </a> </td> </tr> </table>

## 📝 Licença | License
Este projeto é open source e livre para qualquer pessoa usar, modificar e distribuir para fins educacionais e pessoais.
This project is open source and free for anyone to use, modify, and distribute for educational and personal purposes.

Veja o arquivo:
See the file:
[LICENSE](LICENSE)

## 🎯 Motivação | Motivation

Este projeto foi criado como um desafio pessoal para aprender mais sobre:
This project was created as a personal challenge to learn more about:
- Python
- RSS Feeds
- Discord Bots
- Automação | Automation
- Manipulação de dados | Data handling
