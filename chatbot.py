from dotenv import load_dotenv
import os
import telebot
import requests

import speech_recognition as sr
from pydub import AudioSegment

from haystack.components.generators.chat import HuggingFaceTGIChatGenerator
from haystack.dataclasses import ChatMessage

# Last 10 chat conversations
msg = []

# Load environment variables from .env file
load_dotenv()

# Set Hugging Face API token
os.environ["HF_API_TOKEN"] = os.getenv("HF_API_TOKEN")

# Initialize Hugging Face Chat Generator
generator = HuggingFaceTGIChatGenerator(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    generation_kwargs={"max_new_tokens": 350},
)

generator.warm_up()

# Initialize Telegram Bot
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


# Start command
@bot.message_handler(commands=["start"])
def start_bot(message):
    bot.reply_to(message, "Welcome to Sania ChatBOT! What do you need help with?")


# Help command
@bot.message_handler(commands=["help"])
def bot_help(message):
    bot.reply_to(
        message,
        "Start typing to chat with Sania bot 🤖. \n\n You can also send voice messages to chat with Sania bot.",
    )


# Handle text messages
@bot.message_handler(func=lambda message: message.text)
def handle_text(message):
    msg.append(ChatMessage.from_user(message.text))
    response = generator.run(messages=msg)
    msg.append(response["replies"][0])
    bot.reply_to(message, response["replies"][0].content)
    if len(msg) > 20:
        msg.pop(0)
        msg.pop(0)

@bot.message_handler(commands=["feedback"])
def bot_feedback(message):
    # Add code to collect user feedback
    user_feedback = message.text.replace("/feedback", "").strip()
    
    # Implement your feedback handling logic here, e.g., store it in a database
    # For demonstration purposes, we'll just reply with a generic thank-you message
    bot.reply_to(message, "Thank you for your feedback! We appreciate your input.")

    # You can also log the feedback for further analysis or improvement
    print(f"User Feedback: {user_feedback}")


if __name__ == "__main__":
    print("Bot is running...")
    print("Press Ctrl + C to stop bot")
    bot.polling()