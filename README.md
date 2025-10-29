# Telegram AI Chatbot (FastAPI + Groq + Render Deployment)

A conversational **Telegram bot** powered by **Groq’s LLaMA 3 model**, built using **FastAPI** and deployed on **Render**.  
The bot chats naturally with users and can even reply using **Text-to-Speech (TTS)** voice messages! 🎤

---

## Live Demo

** Bot Link:** [@imafresher_bot](https://t.me/imafresher_bot)

** Backend Hosted At:** [https://telegram-ai-chatbot-6pan.onrender.com](https://telegram-ai-chatbot-6pan.onrender.com)

---

## Tech Stack

-  **Python 3**
-  **FastAPI** – Backend API framework  
-  **Groq API (LLaMA 3.1 8B)** – AI model for generating chat replies  
-  **Telegram Bot API** – Handles user messages and responses  
-  **gTTS (Google Text-to-Speech)** – Converts text replies into audio messages  
-  **Render** – Cloud hosting and webhook management  

---

## Features

 Real-time Telegram chat  
 AI-generated responses using **LLaMA 3 (Groq API)**  
 Text + Voice replies (TTS)  
 Context-aware conversation history  
 Deployed on Render using FastAPI + Webhook integration  
 Secure secret management using environment variables  

---

##  Project Setup (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/apekshatangod/telegram-ai-chatbot.git
cd telegram-ai-chatbot
```
###2. Create a Virtual Environment
```bash
# For macOS/Linux
python -m venv venv
source venv/bin/activate

# For Windows
venv\Scripts\activate
```
###3. Install Dependencies
```bash
pip install -r requirements.txt
```
###4. Create a .env File

⚠️ Only required for local testing.
Create a file named .env in the root directory with:
```
GROQ_API_KEY=your_groq_api_key_here
TELEGRAM_TOKEN=your_telegram_bot_token_here
WEBHOOK_BASE=https://your-local-or-render-url
WEBHOOK_PATH_SECRET=your_password_here
VOICE_ENABLED=true
PORT=8000
```
###5. Run the App Locally
```bash
python main.py
```
### Deployment on Render
This bot is fully deployed and live on Render using a webhook integration.
Build Command:
```bash
pip install -r requirements.txt
```
Start Command:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
Environment Variables:
```
GROQ_API_KEY
TELEGRAM_TOKEN
WEBHOOK_BASE
PORT
```
### Set Webhook (Example Command)
```
curl -X POST "https://api.telegram.org/bot<YOUR_TELEGRAM_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-render-app-url.onrender.com/webhook/<YOUR_TELEGRAM_TOKEN>"}'
```
Example Interaction

User:
```
Hello bot!
```
Bot:
```
Hey there 👋 I’m your friendly AI assistant powered by Groq!
(Also sends a voice message of the same reply 🎧)
```
###  Author

**Apeksha V Tangod**  
GitHub: [@apekshatangod](https://github.com/apekshatangod)
