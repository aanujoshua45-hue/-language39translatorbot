# Language39 Translator Bot

🤖 A powerful Telegram translation bot supporting 27+ languages.

## Features

- 🌍 Translate between 27+ languages
- 🔍 Auto-detect source language
- 💾 Save user language preferences
- 🎨 Inline keyboard interface
- ⚡ Fast and reliable

## Supported Languages

English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Arabic, Hindi, Bengali, Urdu, Persian, Turkish, Dutch, Polish, Ukrainian, Vietnamese, Thai, Indonesian, Malay, Swahili, Hausa, Yoruba, Igbo

## Deployment on Railway

### Step 1: Create Bot on Telegram
1. Search for `@BotFather` on Telegram
2. Send `/newbot`
3. Name: `Language39 Translator`
4. Username: `language39translatorbot`
5. Copy the API token

### Step 2: Deploy on Railway
1. Fork this repository to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variable:
   - `TELEGRAM_BOT_TOKEN` = your bot token

### Step 3: Test Your Bot
1. Open Telegram
2. Search for your bot username
3. Send `/start` command

## Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/language39-translator-bot.git
cd language39-translator-bot

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export TELEGRAM_BOT_TOKEN=your_bot_token

# Run bot
python bot.py
