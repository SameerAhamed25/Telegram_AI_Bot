from dotenv import load_dotenv
import os
import telebot
import requests
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from telebot import types
from collections import deque
import threading

import speech_recognition as sr
from pydub import AudioSegment

from haystack.components.generators.chat import HuggingFaceTGIChatGenerator
from haystack.dataclasses import ChatMessage
from pydub import AudioSegment
from moviepy.editor import AudioFileClip

# Set the path to FFmpeg and FFprobe manually
ffmpeg_path = r"C:\Users\mdsng\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-6.1.1-full_build\bin\ffmpeg.exe"
ffprobe_path = r"C:\Users\mdsng\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-6.1.1-full_build\bin\ffprobe.exe"

AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

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
    with lock:
        msg.append(ChatMessage.from_user(message.text))
        response = generator.run(messages=list(msg))  # Pass stored chat history to the generator
        msg.append(response["replies"][0])
        bot.reply_to(message, response["replies"][0].content)
        
# Function to handle voice messages
@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    print("Handling voice message...")

    # Download voice message
    voice_file = bot.get_file(message.voice.file_id)
    file = requests.get(
        "https://api.telegram.org/file/bot{0}/{1}".format(TOKEN, voice_file.file_path)
    )
    with open("audio.ogg", "wb") as f:
        f.write(file.content)

    # Convert voice message to .wav format
    sound = AudioFileClip("audio.ogg")
    sound.write_audiofile("audio.wav")

    print("Voice message converted to .wav")

    # Convert voice meassage to text message
    recognizer = sr.Recognizer()
    with sr.AudioFile("audio.wav") as source:
        audio_file = recognizer.record(source)
        query = recognizer.recognize_google(audio_file)

    print(f"Converted voice message to text: {query}")

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

# Function to handle image messages
@bot.message_handler(content_types=["photo"])
def handle_image(message):
    print("Handling image message...")

    # Download image
    image_file = bot.get_file(message.photo[-1].file_id)
    image_path = os.path.join("images", f"{message.message_id}.jpg")
    image_path = "image.jpg"
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(image_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Get caption from the image
    image_caption = generate_image_caption(image_path)

    # Reply with the image caption
    bot.reply_to(message, image_caption)

    # Optionally, you can remove the downloaded image
    os.remove(image_path)

# Function to generate image caption
def generate_image_caption(image_path):
    print("Generating image caption...")

    # Open the image using PIL
    image = Image.open(image_path)

    # Ensure the image is in RGB mode
    if image.mode != "RGB":
        image = image.convert("RGB")

    try:
        # Process the image
        image_caption = BlipProcessor(images=image, return_tensors="pt")
        print("Image caption generated successfully.")
        return image_caption
    except Exception as e:
        print("Error generating image caption:", e)
        return None

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

# Start the bot
if __name__ == "__main__":
    print("Bot is running...")
    print("Press Ctrl + C to stop bot")
    bot.polling()
