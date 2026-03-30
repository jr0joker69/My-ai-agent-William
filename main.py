import os
import logging
import requests
import feedparser
import schedule
import time
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
CHANNEL = "@BYTEREPORT"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def ask_groq(prompt):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1024}
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=20)
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {e}"

RSS_FEEDS = ["https://techcrunch.com/feed/", "https://feeds.feedburner.com/TheHackersNews", "https://www.wired.com/feed/rss"]
posted_links = set()

def fetch_and_post_news():
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]:
                link = entry.get("link", "")
                if link in posted_links:
                    continue
                title = entry.get("title", "")
                summary = entry.get("summary", "")[:400]
                prompt = f"You are ByteReport tech news editor. Format professionally:
Title: {title}
Summary: {summary}
Rules: emoji+category, 3-4 lines, Why it matters, 3 hashtags"
                formatted = ask_groq(prompt)
                if formatted:
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHANNEL, "text": formatted}, timeout=10)
                    posted_links.add(link)
                    time.sleep(30)
        except Exception as e:
            logger.error(f"Feed error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Thinking...")
    response = ask_groq(update.message.text)
    await update.message.reply_text(response)

async def post_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Posting news now...")
    threading.Thread(target=fetch_and_post_news).start()

def run_scheduler():
    schedule.every(4).hours.do(fetch_and_post_news)
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=run_scheduler, daemon=True).start()
    bot = ApplicationBuilder().token(BOT_TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("postnow", post_now))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot.run_polling()

if __name__ == "__main__":
    main()
