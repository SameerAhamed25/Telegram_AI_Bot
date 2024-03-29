## Overview

This is a chatbot created using Python, Haystack, pydub, and the Hugging Face model `mistralai/Mistral-7B-Instruct-v0.2`. It supports text and voice messages, allowing users to interact with the chatbot in their preferred format.
The **Sania Telegram Bot** is a conversational AI bot built using Python and the Telegram Bot API. It allows users to interact with the Mistral model to get responses to their messages, including text, voice and send timed messages.

**Unlinke Other Bots this Bot can Remember the conversations within the sessions. We can change how many conversations it can save in the code.**
**It can also send timed messages specified by the user using chat id of the recipient**

## Prerequisites

- Hugging Face Token
- Telegram Bot Token

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/renuka010/Mistral-Telegram-Bot.git
    ```
2. Change into the project directory:
    ```bash
    cd Mistral-Telegram-Bot
    ```
3. Create and Activate the virtual environment:
    ```bash
    python3 -m venv venv  # Create
    venv\Scripts\activate    # Activate
    ```
4. Install the dependencies in the virtual environment:
    ```bash
    pip install -r requirements.txt
    ' and others specified in the notion doc.'
    ```
5. Create a `.env` file with your Huggingface token and Telegram token:
    ```
    HF_API_TOKEN=your_huggingface_token
    TELEGRAM_BOT_TOKEN=your_telegram_token
    ```
6. Run the server:
    ```bash
    python chatbot.py
    ```

## Features

- **Text Input**: Users can send text messages to the bot to initiate a conversation or ask questions. The Bot excels in maintaining continuity within conversations, seamlessly remembering previous interactions within the same session to provide users with a personalized and coherent experience.
- **Voice Input**: Users can send voice messages to the bot, which will be transcribed to text for processing.
- **Timed Messages**: The bot also has the ability to send timed messages to users. This can be set up to provide periodic reminders or updates, enhancing the interaction experience.

## Inputs

The Bot accepts the following inputs:

1. **Text Messages**: Users can send text messages containing their queries or messages.
2. **Voice Messages**: Users can send voice messages containing their queries or messages.

## Outputs

The Bot provides the following outputs:

1. **Text Responses**: The bot responds to user messages with text-based replies.
2. **Voice Responses**: The bot may provide voice responses for voice inputs or text inputs, allowing for a conversational experience.

## Usage

To use the Mistral Telegram Bot, follow these steps:

1. **Start the Bot**: Start a conversation with the bot by searching for it on Telegram and sending a message.
2. **Send Messages**: Send text messages, voice messages to the bot to initiate conversations or ask questions.
3. **Receive Responses**: The bot will respond to your messages with relevant information or responses.


This bot is created on the basis of -> https://github.com/renuka010/Mistral-Telegram-Bot.git, basicaly this an updated and more effective version.
For this to work we need to install and import more packages other than that mentioned in the requirements.txt!

Check Out Notion Notes For More Details:
https://www.notion.so/Telegram-AI-Bot-Sam-57802ddc637147008e1fb0d6bd7a8bbd?pvs=4
