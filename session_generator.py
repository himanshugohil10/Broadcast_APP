import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# Load variables if they exist in .env
load_dotenv()

async def generate_string_session():
    print("--- Telegram String Session Generator ---")
    
    # Get credentials
    api_id = os.getenv("TG_API_ID") or input("Enter API ID: ")
    api_hash = os.getenv("TG_API_HASH") or input("Enter API Hash: ")
    
    print("\nConnecting... (Check your Telegram app for the login code)")
    
    # Generate Session
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.start()
    
    # Get the string
    session_string = client.session.save()
    
    # SAVE TO FILE TO PREVENT COPY-PASTE ERRORS
    with open("session_string.txt", "w") as f:
        f.write(session_string)
        
    print("\n---------------------------------------")
    print("✅ SUCCESS! Session string saved to 'session_string.txt'")
    print("---------------------------------------")
    print("1. Open 'session_string.txt' with Notepad.")
    print("2. Copy the ENTIRE text (Ctrl+A -> Ctrl+C).")
    print("3. Paste it into your Streamlit Secrets.")
    
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(generate_string_session())

'''

#### **Step 2: Generate & Copy**
1.  Run the new script: `python session_generator.py`
2.  Login again.
3.  Open the newly created file `session_string.txt`.
4.  Copy the **exact** content.

#### **Step 3: Update Streamlit Secrets**
Go back to your Streamlit App Dashboard -> Settings -> Secrets and update the variable.

**Make sure it looks like this (no extra spaces inside the quotes):**

```toml
'''