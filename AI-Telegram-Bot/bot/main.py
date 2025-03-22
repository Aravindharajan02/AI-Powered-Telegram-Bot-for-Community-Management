import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from transformers import pipeline
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("config/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Load AI Model
generator = pipeline("text-generation", model="distilgpt2")

# Command: Start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I'm an AI-powered open-source bot. Use /help to see commands.")

# Command: Help
async def help_command(update: Update, context: CallbackContext):
    help_text = (
        "/start - Start bot\n"
        "/faq - Frequently Asked Questions\n"
        "/leaderboard - View top users\n"
        "/reward - Earn engagement points\n"
        "/inspire - Get an inspirational message"
    )
    await update.message.reply_text(help_text)

# AI Chatbot Response
async def chat(update: Update, context: CallbackContext):
    user_input = update.message.text
    response = generator(user_input, max_length=50)[0]['generated_text']
    await update.message.reply_text(response)

# Command: FAQ
async def faq(update: Update, context: CallbackContext):
    faqs = db.collection('faq').stream()
    response = "\n".join([f"{doc.to_dict()['question']}: {doc.to_dict()['answer']}" for doc in faqs])
    await update.message.reply_text(response)

# Command: Leaderboard
async def leaderboard(update: Update, context: CallbackContext):
    users = db.collection("users").order_by("points", direction=firestore.Query.DESCENDING).limit(10).stream()
    leaderboard_text = "\n".join([f"{doc.to_dict()['username']}: {doc.to_dict()['points']} points" for doc in users])
    await update.message.reply_text(f"🏆 Leaderboard 🏆\n\n{leaderboard_text}")

# Command: Reward Users
async def reward_user(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_ref = db.collection("users").document(str(user_id))
    
    user = user_ref.get().to_dict()
    new_points = user.get("points", 0) + 10  # +10 points for engagement
    
    user_ref.set({"points": new_points}, merge=True)
    await update.message.reply_text(f"🎉 You've earned 10 points! Your total: {new_points} points.")

# Start Telegram Bot
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("faq", faq))
app.add_handler(CommandHandler("leaderboard", leaderboard))
app.add_handler(CommandHandler("reward", reward_user))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
