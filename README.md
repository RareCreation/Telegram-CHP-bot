# Telegram-CHP-bot

This repository contains a Telegram bot built using `aiogram`.

## 📌 How to Create a Telegram Bot

1. Open Telegram and search for **BotFather**.
2. Start a chat and send the command:
   ```
   /newbot
   ```
3. Follow the instructions:
   - Choose a name for your bot.
   - Choose a unique username (must end in `bot`).
4. After completion, BotFather will provide a **token**. Save it securely.

## 📦 Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/RarchikCreation/Telegram-CHP-bot.git
   cd Telegram-CHP-bot
   ```

2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the data folder and add your bot token:
   ```
   TOKEN=your-telegram-bot-token
   GMAIL=YOUR_MAIL
   PASSWORD=YOUR APP PASSWORD
   ```
## 🔐 How to Enable 2FA and Create an App Password for Gmail

To use Gmail with your Telegram bot, you need to enable **2-Step Verification** and create an **App Password**.

### ✅ Step 1: Enable 2-Step Verification (2FA)

1. Go to your Google Account: [https://myaccount.google.com](https://myaccount.google.com)
2. In the left sidebar, click on **Security**.
3. Under **"Signing in to Google"**, find **2-Step Verification** and click **Get started**.
4. Follow the steps to set up 2FA using your phone or an authenticator app.

### 🔑 Step 2: Generate an App Password

1. After enabling 2FA, go back to the **Security** section of your Google Account.
2. Under **"Signing in to Google"**, click on **App passwords**.
3. You may need to re-enter your password.
4. In the **Select app** dropdown, choose **Mail**.
5. In the **Select device** dropdown, choose **Other (Custom name)** and enter a name like `Steam`.
6. Click **Generate**.
7. Google will display a 16-character app password. **Copy it** and use it in your `.env` file:

   ```
   GMAIL=your-email@gmail.com
   PASSWORD=your-16-character-app-password
   ```

## 🚀 Running the Bot

Start the bot using:
```sh
python main.py
```

## 🛠 Technologies Used
- Python
- Aiogram
- Asyncio
- Dotenv
- Smtplib
