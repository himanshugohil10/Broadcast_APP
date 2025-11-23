📢 Multi-Channel Broadcaster (Telegram & Email)

A Streamlit-based application to send bulk asynchronous messages to Telegram users (via your personal account) and Emails (via Gmail) concurrently.

Designed for efficiency and safety, this tool handles Indian phone number formatting automatically, manages rate limits to prevent Telegram bans, and provides real-time progress logs.

✨ Features

Dual Channel: Sends Telegram messages and Emails simultaneously.

Asynchronous: Uses Python's asyncio for non-blocking operations.

Smart Formatting: Automatically fixes Excel scientific notation (e.g., 9.18E+12) and formats Indian numbers to +91.

Safety First: Includes random delays (1.5s - 3s) to prevent Telegram flood bans.

Cloud Ready: Works locally with .env and on Streamlit Cloud using Secrets.

Session Management: Uses StringSession for secure, file-free authentication on the cloud.

🛠️ Prerequisites

Python 3.8+ installed.

Telegram API Credentials:

Go to my.telegram.org.

Log in and go to API development tools.

Create a new app to get your API_ID and API_HASH.

Gmail App Password:

Go to Google Account Security.

Enable 2-Step Verification.

Search for App Passwords and create one named "Broadcaster". Copy the 16-character code.

📥 Installation

Clone the repository:

git clone [https://github.com/yourusername/your-repo.git](https://github.com/yourusername/your-repo.git)
cd your-repo


Install dependencies:

pip install -r requirements.txt


⚙️ Configuration (Local Setup)

To run this on your own machine, you need to generate a session string and set up your environment variables.

1. Generate Telegram Session String

You cannot use a generic login locally because 2FA requires interaction. We use a helper script to generate a permanent session string.

Create a .env file in the root folder (or rename .env.example if you have one).

Add your API credentials to .env:

TG_API_ID=12345678
TG_API_HASH=your_long_hash_here


Run the generator:

python session_generator.py


Follow the prompts (Phone number, Login code).

Copy the long string it outputs and paste it into your .env file as TG_SESSION_STRING.

2. Finalize .env file

Your .env file should look like this:

TG_API_ID=12345678
TG_API_HASH=your_long_hash_here
TG_SESSION_STRING=1ApWapz... (very long string) ...
GMAIL_USER=your_email@gmail.com
GMAIL_PASS=xxxx xxxx xxxx xxxx  # Your 16-char App Password
EMAIL_SUBJECT=Important Update


🚀 Usage

Running Locally

Ensure data.xlsx is in the root directory.

Run the app:

streamlit run app.py


The browser will open. Type your message and hit Start Broadcast.

Input Data Format (data.xlsx)

The Excel file must have exactly these headers:

telegram_id

email

9892212345

user1@example.com

9.18E+12

user2@test.com

+91 9999900000

user3@gmail.com

telegram_id: Can be raw numbers, scientific notation, or formatted strings. The app extracts the last 10 digits and adds +91.

email: Valid email address.

☁️ Deployment (Streamlit Cloud)

Push your code to GitHub (Ensure .env is NOT uploaded; check your .gitignore).

Go to Streamlit Community Cloud.

Deploy the app from your repository.

Crucial Step: Go to App Settings -> Secrets.

Paste your configuration in TOML format:

TG_API_ID = "12345678"
TG_API_HASH = "your_long_hash_here"
TG_SESSION_STRING = "your_very_long_string_generated_locally"
GMAIL_USER = "your_email@gmail.com"
GMAIL_PASS = "your_app_password"
EMAIL_SUBJECT = "Update"


Reboot the app.

⚠️ Important Safety Notes

FloodWait Errors: If you see "FloodWait", it means Telegram has temporarily rate-limited your account. Pause for the requested seconds.

Account Safety: This tool automates a User Account (not a Bot). Do not use it for spamming strangers. Only message people who have agreed to be contacted, or you risk getting your account banned.

Delay: Do not remove the asyncio.sleep delay in the code. It is there to protect your account.

📝 Troubleshooting

"Session Invalid" error: Rerun python session_generator.py locally to get a fresh string, then update your .env or Streamlit Secrets.

Message sent to Email but not Telegram: Check the logs. If the number is invalid or privacy settings block non-contacts, it will show "Invalid/Not found".

FileNotFoundError: Ensure data.xlsx exists in the repository (if on Cloud) or local folder.
