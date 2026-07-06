import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from deep_translator import GoogleTranslator

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== CONFIG ====================
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
    sys.exit(1)

logger.info("✅ Bot token loaded successfully")

# ==================== DATA ====================
user_languages = {}

LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'tr': 'Turkish',
    'nl': 'Dutch',
    'pl': 'Polish',
    'uk': 'Ukrainian',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'id': 'Indonesian',
    'ms': 'Malay',
    'sw': 'Swahili',
    'ha': 'Hausa',
    'yo': 'Yoruba',
    'ig': 'Igbo'
}

# ==================== HELPERS ====================
def get_user_lang(user_id):
    return user_languages.get(user_id, 'en')

def get_lang_name(code):
    return LANGUAGES.get(code, code)

# ==================== COMMANDS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_languages:
        user_languages[user_id] = 'en'
    
    current_lang = get_user_lang(user_id)
    current_lang_name = get_lang_name(current_lang)
    
    text = f"""
🤖 *Language39 Translator Bot*

Hello {user.first_name}! 👋

Send me any text and I'll translate it!

🌍 *Your target language:* {current_lang_name}

📝 *Commands:*
/setlang - Change language
/help - Show help
/languages - List all languages
"""
    
    keyboard = [[
        InlineKeyboardButton("🌍 Change Language", callback_data='change_lang'),
        InlineKeyboardButton("📖 Help", callback_data='help')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📖 *Help*

*Commands:*
/start - Welcome message
/help - This menu
/setlang - Change language
/languages - List all languages
/about - About this bot

*How to use:*
Just send any text and I'll translate it!

Example:
Send: "Hello"
Reply: Translation in your chosen language
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def setlang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_lang = get_user_lang(user_id)
    
    keyboard = []
    row = []
    
    for code, name in sorted(LANGUAGES.items()):
        display = f"✅ {name}" if code == current_lang else name
        row.append(InlineKeyboardButton(display, callback_data=f'lang_{code}'))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🌍 *Select your language*\nCurrent: {get_lang_name(current_lang)}",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🌍 *Supported Languages*\n\n"
    for code, name in sorted(LANGUAGES.items()):
        text += f"• {name} (`{code}`)\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🤖 *Language39 Translator Bot*

Version: 1.0.0
Powered by: Google Translate API

Translate between 27+ languages with auto-detection!

Made with ❤️ for Language39 Project
"""
    await update.message.reply_text(text, parse_mode='Markdown')

# ==================== TRANSLATE ====================

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    target_lang = get_user_lang(user_id)
    target_lang_name = get_lang_name(target_lang)
    
    await update.message.chat.send_action(action="typing")
    
    try:
        # Detect source
        try:
            detected = GoogleTranslator().detect(text)
            detected_name = get_lang_name(detected)
        except:
            detected_name = "Unknown"
        
        # Translate
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        
        response = f"""
🔄 *Translation to {target_lang_name}*

📝 *Original:*
{text}

✅ *Translated:*
{translated}

ℹ️ *Detected:* {detected_name}
"""
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text("❌ Translation failed. Please try again.")

# ==================== BUTTONS ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()
    
    data = query.data
    
    if data == 'change_lang':
        current_lang = get_user_lang(user_id)
        
        keyboard = []
        row = []
        for code, name in sorted(LANGUAGES.items()):
            display = f"✅ {name}" if code == current_lang else name
            row.append(InlineKeyboardButton(display, callback_data=f'lang_{code}'))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🌍 *Select your language*\nCurrent: {get_lang_name(current_lang)}",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    elif data == 'help':
        text = """
📖 *Help*

*Commands:*
/start - Welcome message
/help - This menu
/setlang - Change language
/languages - List all languages
/about - About this bot

*How to use:*
Just send any text and I'll translate it!
"""
        await query.edit_message_text(text, parse_mode='Markdown')
        
    elif data == 'back':
        user = update.effective_user
        current_lang = get_user_lang(user_id)
        current_lang_name = get_lang_name(current_lang)
        
        text = f"""
🤖 *Language39 Translator Bot*

Hello {user.first_name}! 👋

Send me any text and I'll translate it!

🌍 *Your target language:* {current_lang_name}

📝 *Commands:*
/setlang - Change language
/help - Show help
/languages - List all languages
"""
        keyboard = [[
            InlineKeyboardButton("🌍 Change Language", callback_data='change_lang'),
            InlineKeyboardButton("📖 Help", callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        
    elif data.startswith('lang_'):
        lang_code = data.replace('lang_', '')
        if lang_code in LANGUAGES:
            user_languages[user_id] = lang_code
            lang_name = get_lang_name(lang_code)
            await query.edit_message_text(
                f"✅ Language changed to *{lang_name}*!\n\nSend me any text to translate.",
                parse_mode='Markdown'
            )

# ==================== ERROR ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# ==================== MAIN ====================

def main():
    logger.info("🚀 Starting Language39 Translator Bot...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("setlang", setlang))
    app.add_handler(CommandHandler("languages", languages))
    app.add_handler(CommandHandler("about", about))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    app.add_error_handler(error_handler)
    
    logger.info("✅ Bot is running!")
    app.run_polling()

if __name__ == '__main__':
    main()
