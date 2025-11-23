import streamlit as st
import pandas as pd
import asyncio
import random
import os
import re
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# --- CONFIGURATION LOADER ---
# 1. Load variables from .env file (if it exists)
load_dotenv()

def get_config(key):
    """
    Smart config loader (Fixed for Local Testing):
    1. Checks OS Environment Variables (Local .env) FIRST.
    2. Checks Streamlit Secrets (Cloud) SECOND.
    This prevents 'FileNotFoundError' locally where secrets.toml doesn't exist.
    """
    # 1. Try Local .env
    value = os.getenv(key)
    if value:
        return value
    
    # 2. Try Streamlit Secrets (Cloud fallback)
    # We wrap this in a try-block because accessing st.secrets
    # can crash locally if no secrets.toml file exists.
    try:
        if key in st.secrets:
            return st.secrets[key]
    except FileNotFoundError:
        pass # No secrets file found locally, that's fine
    except Exception:
        pass
        
    return None

# Load Credentials
API_ID = get_config("TG_API_ID")
API_HASH = get_config("TG_API_HASH")
SESSION_STR = get_config("TG_SESSION_STRING")
GMAIL_USER = get_config("GMAIL_USER")
GMAIL_PASS = get_config("GMAIL_PASS")
EMAIL_SUBJECT = get_config("EMAIL_SUBJECT") or "Update"

# File Check logic
DATA_FILE = 'data.xlsx'

st.set_page_config(page_title="Broadcaster", layout="centered")
st.title("📢 Global Broadcaster")

# --- VALIDATION ---
missing_vars = []
if not API_ID: missing_vars.append("TG_API_ID")
if not SESSION_STR: missing_vars.append("TG_SESSION_STRING")
if not GMAIL_PASS: missing_vars.append("GMAIL_PASS")

if missing_vars:
    st.error(f"❌ Missing Configuration: {', '.join(missing_vars)}")
    st.info("Locally: Check your .env file.\nCloud: Check Streamlit Secrets.")
    st.stop()

# --- HELPER: PHONE NUMBER CLEANER ---
def clean_indian_phone(value):
    if pd.isna(value) or value == '': return None
    try:
        str_val = str(int(float(value))) 
    except:
        str_val = str(value)
    digits_only = re.sub(r'\D', '', str_val)
    if len(digits_only) < 10: return None
    return f"+91{digits_only[-10:]}"

# --- ASYNC FUNCTIONS ---
async def send_telegram(client, phone_number, message):
    try:
        # Use direct ID resolution for speed/privacy handling
        entity = await client.get_input_entity(phone_number)
        await client.send_message(entity, message)
        return True, "Sent"
    except ValueError:
        return False, "Invalid/Not found"
    except errors.FloodWaitError as e:
        return False, f"FloodWait {e.seconds}s"
    except errors.UserPrivacyRestrictedError:
        return False, "Privacy Restricted"
    except Exception as e:
        return False, str(e)

async def send_email(smtp_client, recipient, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"] = GMAIL_USER
    msg["To"] = recipient
    try:
        await smtp_client.send_message(msg)
        return True, "Sent"
    except Exception as e:
        return False, str(e)

async def run_broadcast_process(df, message_content):
    status_box = st.info("Initializing connection...")
    progress_bar = st.progress(0)
    log_area = st.empty()
    logs = []
    stats = {"tg_ok": 0, "tg_fail": 0, "em_ok": 0, "em_fail": 0}

    # 1. Connect Telegram (Using StringSession)
    try:
        client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            st.error("❌ Session String Invalid/Expired. Regen via session_generator.py")
            return
    except Exception as e:
        st.error(f"❌ Telegram Connection Failed: {e}")
        return

    # 2. Connect Gmail
    try:
        smtp = aiosmtplib.SMTP(hostname="smtp.gmail.com", port=587, start_tls=True)
        await smtp.connect()
        await smtp.login(GMAIL_USER, GMAIL_PASS)
    except Exception as e:
        st.error(f"❌ Gmail Login Failed: {e}")
        await client.disconnect()
        return

    status_box.info("🚀 Sending messages...")
    total = len(df)
    
    for index, row in df.iterrows():
        phone_number = clean_indian_phone(row.get('telegram_id'))
        email = row.get('email')
        
        tasks = []
        
        if phone_number: tasks.append(send_telegram(client, phone_number, message_content))
        else: tasks.append(asyncio.sleep(0))

        if pd.notna(email): tasks.append(send_email(smtp, email, message_content))
        else: tasks.append(asyncio.sleep(0))

        results = await asyncio.gather(*tasks)
        
        tg_res = results[0] if phone_number else (False, "Bad Format")
        em_res = results[1] if pd.notna(email) else (False, "-")

        if phone_number:
            if tg_res[0]: stats["tg_ok"] += 1
            else: stats["tg_fail"] += 1
        if pd.notna(email):
            if em_res[0]: stats["em_ok"] += 1
            else: stats["em_fail"] += 1

        logs.insert(0, f"Row {index+1}: {phone_number or 'Bad Num'} -> {tg_res[1]} | {email} -> {em_res[1]}")
        log_area.text_area("Live Logs", "\n".join(logs[:15]), height=200)
        progress_bar.progress((index + 1) / total)
        await asyncio.sleep(random.uniform(1.5, 3.0))

    await client.disconnect()
    await smtp.quit()
    
    status_box.empty()
    progress_bar.empty()
    st.success("✅ Broadcast Complete!")
    c1, c2 = st.columns(2)
    c1.metric("Telegram", stats['tg_ok'], delta=f"-{stats['tg_fail']} fail")
    c2.metric("Email", stats['em_ok'], delta=f"-{stats['em_fail']} fail")

# --- UI LOGIC ---
with st.form("msg_form"):
    st.write("### Compose Message")
    msg_input = st.text_area("Message Content", height=150)
    btn_send = st.form_submit_button("Start Broadcast")

if btn_send:
    if not msg_input.strip():
        st.warning("⚠️ Message is empty!")
    elif not os.path.exists(DATA_FILE):
        st.error(f"❌ '{DATA_FILE}' not found in repo.")
    else:
        try:
            df = pd.read_excel(DATA_FILE)
            asyncio.run(run_broadcast_process(df, msg_input))
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
'''

### **Double Check Your `.env`**
Make sure your `.env` file is in the **same folder** as `app.py` and looks exactly like this (without quotes):

```text
TG_API_ID=123456
TG_API_HASH=a1b2c3d4e5.
TG_SESSION_STRING=1ApWapz...
GMAIL_USER=example@gmail.com
GMAIL_PASS=your_app_password'''