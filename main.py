import os
import json
import logging
import httpx
import asyncio
import io
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from gtts import gTTS


# LOAD ENVIRONMENT VARIABLES
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE", "")
WEBHOOK_PATH_SECRET = os.getenv("WEBHOOK_PATH_SECRET", "secret123")
PORT = int(os.getenv("PORT", 8000))

# Validate essential config
if not GROQ_API_KEY or not TELEGRAM_TOKEN:
    raise RuntimeError("❌ Missing GROQ_API_KEY or TELEGRAM_TOKEN in .env file")

# CONSTANTS
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# FASTAPI APP + LOGGER
app = FastAPI(title="Telegram AI Chatbot (Groq)")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# 🧠 In-memory conversation history
conversations = {}  # Stores chat history: {chat_id: [messages]}

# GROQ CHAT COMPLETION
async def call_groq_chat(messages):
    """Send messages to Groq API and get AI reply."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-8b-instant",  # free & fast model
                    "messages": messages,
                    "max_tokens": 256,
                    "temperature": 0.8,
                },
            )

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            logger.error(f"Groq API error: {response.status_code} {response.text}")
            return "⚠️ Sorry, I’m having trouble thinking right now!"
    except Exception as e:
        logger.error(f"Groq API exception: {e}")
        return "⚠️ Something went wrong while generating a response."

# SEND MESSAGE TO TELEGRAM
async def send_telegram_message(chat_id, text):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{TELEGRAM_API_URL}/sendMessage",
                json={"chat_id": chat_id, "text": text},
            )
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

# HANDLE TELEGRAM UPDATES
@app.post("/webhook/{token}")
async def telegram_webhook(request: Request, token: str):
    """Webhook endpoint that Telegram will send messages to."""
    if token != TELEGRAM_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    data = await request.json()
    asyncio.create_task(process_update(data))
    return {"ok": True}

# PROCESS INCOMING MESSAGE
async def process_update(update):
    try:
        message = update.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if not text or not chat_id:
            return

        user = message.get("from", {}).get("username", "user")
        logger.info(f"Message from @{user}: {text}")

        # Handle /start
        if text.lower() == "/start":
            await send_telegram_message(
                chat_id,
                "👋 Hey there! I’m your friendly AI chatbot powered by Groq (Llama 3). Just say something!",
            )
            return

        # 🧠 Maintain conversation memory per user
        if chat_id not in conversations:
            conversations[chat_id] = [
                {"role": "system", "content": "You are a helpful and friendly Telegram chatbot."}
            ]

        # Add user message to their history
        conversations[chat_id].append({"role": "user", "content": text})

        # Generate AI reply using chat history
        ai_reply = await call_groq_chat(conversations[chat_id])

        # Add AI reply to memory
        conversations[chat_id].append({"role": "assistant", "content": ai_reply})

        # Send reply as text
        await send_telegram_message(chat_id, ai_reply)

        # 🗣️ Optional: Generate Voice Reply
        try:
            tts = gTTS(ai_reply, lang='en')
            voice_file = io.BytesIO()
            tts.write_to_fp(voice_file)
            voice_file.seek(0)

            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice",
                    data={"chat_id": chat_id},
                    files={"voice": ("voice.ogg", voice_file, "audio/ogg")},
                )

            logger.info(f"🎤 Sent voice reply to @{user}")
        except Exception as e:
            logger.error(f"Failed to generate or send voice reply: {e}")

    except Exception as e:
        logger.error(f"Error processing update: {e}")
        if "chat_id" in locals():
            await send_telegram_message(chat_id, "⚠️ An error occurred. Please try again later.")

# SET WEBHOOK
@app.post("/set_webhook")
async def set_webhook():
    """Set Telegram webhook dynamically."""
    webhook_url = f"{WEBHOOK_BASE}/webhook/{TELEGRAM_TOKEN}"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TELEGRAM_API_URL}/setWebhook",
            json={"url": webhook_url},
        )

    if response.status_code == 200:
        logger.info(f"✅ Webhook set successfully → {webhook_url}")
        return {"result": "Webhook set successfully"}
    else:
        logger.error(f"❌ Failed to set webhook: {response.text}")
        return {"error": "Failed to set webhook"}

# ROOT ROUTE
@app.get("/")
async def root():
    return {"message": "🚀 Telegram AI chatbot (Groq) is running!"}

# MAIN ENTRY POINT
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI server on http://localhost:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
