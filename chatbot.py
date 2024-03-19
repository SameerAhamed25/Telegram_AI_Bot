from dotenv import load_dotenv
import os
import telebot
import requests
from collections import deque
import threading
import schedule
import time
import signal
import sys
import speech_recognition as sr
from pydub import AudioSegment
from haystack.components.generators.chat import HuggingFaceTGIChatGenerator
from haystack.dataclasses import ChatMessage
from moviepy.editor import AudioFileClip

# Set the path to FFmpeg and FFprobe manually
ffmpeg_path = r"C:\Users\mdsng\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-6.1.1-full_build\bin\ffmpeg.exe"
ffprobe_path = r"C:\Users\mdsng\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-6.1.1-full_build\bin\ffprobe.exe"

AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# Load environment variables from .env file
dotenv_path = r"C:\Users\mdsng\Mistral-Telegram-Bot\venv\.env.txt"
load_dotenv(dotenv_path)

# Test if the variables are loaded
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
hf_api_token = os.getenv("HF_API_TOKEN")
print("Telegram:", telegram_bot_token, " Hugging Face:", hf_api_token)

# Set Hugging Face API token
os.environ["HF_API_TOKEN"] = hf_api_token

# Initialize Hugging Face Chat Generator
generator = HuggingFaceTGIChatGenerator(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    generation_kwargs={"max_new_tokens": 350},
)

generator.warm_up()

# Initialize Telegram Bot
bot = telebot.TeleBot(telegram_bot_token)

# Last 10 chat conversations
msg = deque(maxlen=20)

# Function to retrieve group message history
def get_group_message_history(chat_id, limit=100):
    messages = bot.get_chat_history(chat_id, limit=limit)
    return messages

# Function to handle the /start command
@bot.message_handler(commands=["start"])
def start_bot(message):
    bot.reply_to(message, "Welcome to Sania ChatBOT! What do you need help with?")

# Function to handle the /help command
@bot.message_handler(commands=["help"])
def bot_help(message):
    bot.reply_to(
        message,
        "Start typing to chat with Sania bot 🤖. \n\n You can also send voice messages to chat with Sania bot.",
    )

# Define a lock for synchronizing access to shared resources
lock = threading.Lock()

# Maximum chat history size
MAX_CHAT_HISTORY = 20

# Shared chat history deque
msg = deque(maxlen=MAX_CHAT_HISTORY)
        
# Function to handle text messages
@bot.message_handler(func=lambda message: message.text)
def handle_text(message):
    # Print the chat ID
    print("Chat ID:", message.chat.id)
    with lock:
        msg.append(ChatMessage.from_user(message.text))
        response = generator.run(messages=list(msg))  # Pass stored chat history to the generator
        msg.append(response["replies"][0])
        bot.reply_to(message, response["replies"][0].content)

# Function to handle voice messages
@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    # Download voice message
    voice_file = bot.get_file(message.voice.file_id)
    file = requests.get(
        "https://api.telegram.org/file/bot{0}/{1}".format(telegram_bot_token, voice_file.file_path)
    )
    with open("audio.ogg", "wb") as f:
        f.write(file.content)

    # Convert voice message to .wav format
    sound = AudioFileClip("audio.ogg")
    sound.write_audiofile("audio.wav")

    # Convert voice message to text message
    recognizer = sr.Recognizer()
    with sr.AudioFile("audio.wav") as source:
        audio_file = recognizer.record(source)
        query = recognizer.recognize_google(audio_file)

    # Get response from Mistral bot
    msg.append(ChatMessage.from_user(query))
    response = generator.run(messages=msg)
    msg.append(response["replies"][0])
    bot.reply_to(message, response["replies"][0].content)

    os.remove("audio.ogg")
    os.remove("audio.wav")
    if len(msg) > 20:
        msg.pop(0)
        msg.pop(0)

# Define a new command to retrieve group message history
@bot.message_handler(commands=["history"])
def get_group_history(message):
    # Retrieve the chat history
    chat_history = get_group_message_history(message.chat.id)

    # Extract and process the messages from the history
    if chat_history:
        # Extract the messages from the history
        messages = [history_item.text for history_item in chat_history]

        # Process the messages, e.g., print them
        for msg in messages:
            print(msg)  # Replace this with your desired processing logic

        # Reply to the user indicating that the history has been retrieved
        bot.reply_to(message, "Group message history retrieved successfully.")
    else:
        # Reply to the user if no history is available
        bot.reply_to(message, "No message history available for this group.")

# Function to send a timed message
def send_timed_message():
    # Replace 'RECIPIENT_ID' with the Telegram ID of the recipient
    recipient_id = '7133305371'
    # Replace 'YOUR_MESSAGE' with the message you want to send
    message = 'This is a timed message from sam !!!'
    # Send the message using your bot
    bot.send_message(recipient_id, message)

# Schedule the timed message to be sent daily at a specific time
schedule.every().day.at("21:53").do(send_timed_message)

# Function to start the scheduler
def start_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=start_scheduler)
scheduler_thread.start()

# Function to handle KeyboardInterrupt
def signal_handler(signal, frame):
    print("Bot stopped by user.")
    bot.stop_polling()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Start the bot
if __name__ == "__main__":
    print("Bot is running...")
    print("Press Ctrl + C to stop bot! ><")
    bot.polling()
