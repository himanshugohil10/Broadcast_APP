import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Load variables if they exist in .env, otherwise prompt user
load_dotenv()

async def generate_string_session():
    print("--- Telegram String Session Generator ---")
    
    api_id = os.getenv("TG_API_ID") or input("Enter API ID: ")
    api_hash = os.getenv("TG_API_HASH") or input("Enter API Hash: ")
    
    # We use StringSession to get a text string instead of a .session file
    client = TelegramClient(StringSession(), api_id, api_hash)
    
    print("\nConnecting... (Check your Telegram for the code)")
    await client.start()
    
    # Get the string
    session_string = client.session.save()
    
    print("\n---------------------------------------")
    print("SUCCESS! COPY THE STRING BELOW INTO YOUR .env FILE:")
    print("---------------------------------------")
    print(f"\nTG_SESSION_STRING={session_string}\n")
    print("---------------------------------------")
    print("Paste this entire line into your .env file or Streamlit Secrets.")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(generate_string_session())