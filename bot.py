import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from deep_translator import GoogleTranslator
from deep_translator.exceptions import NotValidPayload, LanguageNotSupportedException

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== ENVIRONMENT VARIABLES ====================
# Try multiple ways to get the token
BOT_TOKEN = None

# Method 1: Direct environment variable
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Method 2: Check if token is passed as a file (Railway sometimes does this)
if not BOT_TOKEN:
    try:
        with open('/etc/secrets/TELEGRAM_BOT_TOKEN', 'r') as f:
            BOT_TOKEN = f.read().strip()
        logger.info("✅ Token loaded from secrets file")
    except:
        pass

# Method 3: Check for token in Railway's environment
if not BOT_TOKEN:
    # Railway sometimes uses different naming
    for key in os.environ.keys():
        if 'TOKEN' in key.upper() and 'BOT' in key.upper():
            BOT_TOKEN = os.environ.get(key)
            logger.info(f"✅ Token loaded from: {key}")
            break

# If still no token, show helpful error
if not BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
    logger.error("Please add TELEGRAM_BOT_TOKEN to Railway Variables")
    logger.error("Available environment variables:")
    for key in os.environ.keys():
        logger.error(f"  - {key}")
    sys.exit(1)

logger.info(f"✅ Bot token loaded successfully (length: {len(BOT_TOKEN)})")

# ==================== USER DATA STORAGE ====================
user_languages = {}  # user_id: language_code

# ==================== SUPPORTED LANGUAGES ====================
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese (Simplified)',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'fa': 'Persian',
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

# ==================== HELPER FUNCTIONS ====================
def get_user_language(user_id):
    """Get user's preferred target language"""
    return user_languages.get(user_id, 'en')

def get_language_name(code):
    """Get language name from code"""
    return LANGUAGES.get(code, code)

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = user.id
    
    # Set default language for new user
    if user_id not in user_languages:
        user_languages[user_id] = 'en'
    
    current_lang = get_user_language(user_id)
    current_lang_name = get_language_name(current_lang)
    
    welcome_text = f"""
🤖 *Welcome to Language39 Translator Bot!*

Hello {user.first_name}! I'm your personal translation assistant.

🌟 *Features:*
• Translate text to 27+ languages
• Auto-detect source language
• Save your language preference
• Simple and fast

📝 *How to use:*
• Send any text message to translate
• Use /setlang to change target language
• Use /help for all commands

🌍 *Your target language:* {current_lang_name}

Start translating now! 🚀
"""
    
    keyboard = [
        [InlineKeyboardButton("🌍 Change Language", callback_data='change_lang')],
        [InlineKeyboardButton("📖 Help", callback_data='help')],
        [InlineKeyboardButton("ℹ️ About", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    logger.info(f"User {user_id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 *Available Commands*

/start - Welcome and setup
/help - Show this help menu
/setlang - Change target language
/languages - List all supported languages
/about - Bot information

💡 *Quick Guide:*
1. Set your target language with /setlang
2. Send any text message
3. I'll translate it instantly!

*Example:*
Send: "Hello, how are you?"
If target language is Spanish:
Reply: "Hola, ¿cómo estás?"

🔗 *Project:* Language39
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def setlang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setlang command"""
    user_id = update.effective_user.id
    current_lang = get_user_language(user_id)
    current_lang_name = get_language_name(current_lang)
    
    # Create language selection keyboard
    keyboard = []
    row = []
    
    for code, name in sorted(LANGUAGES.items()):
        # Mark current language with checkmark
        display_name = f"✅ {name}" if code == current_lang else name
        row.append(InlineKeyboardButton(display_name, callback_data=f'lang_{code}'))
        
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🌍 *Select Your Target Language*\n\nCurrent: *{current_lang_name}*\n\nChoose from below:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /languages command"""
    lang_list = []
    for code, name in sorted(LANGUAGES.items()):
        lang_list.append(f"• {name} (`{code}`)")
    
    languages_text = f"""
🌍 *Supported Languages*

Total: {len(LANGUAGES)} languages

{chr(10).join(lang_list)}

Use /setlang to change your target language.
"""
    await update.message.reply_text(languages_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = """
🤖 *Language39 Translator Bot*

*Version:* 1.0.0
*Developer:* Language39 Team
*Powered by:* Google Translate API

*Features:*
• Translate between 27+ languages
• Auto language detection
• User preferences saved
• Inline keyboard interface

*Project Website:* language39.com
*GitHub:* github.com/language39/translator-bot

Made with ❤️ for Language39 Project
"""
    await update.message.reply_text(about_text, parse_mode='Markdown')

# ==================== MESSAGE HANDLER ====================

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages - Translate to user's target language"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Get user's target language
    target_lang = get_user_language(user_id)
    target_lang_name = get_language_name(target_lang)
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        # Detect source language
        try:
            detected = GoogleTranslator().detect(text)
            detected_name = get_language_name(detected)
        except:
            detected_name = "Unknown"
        
        # Translate the text
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text)
        
        # Prepare response
        response = f"""
🔄 *Translation to {target_lang_name}*

📝 *Original Text:*
{text}

✅ *Translated Text:*
{translated}

ℹ️ *Detected Source:* {detected_name}
"""
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except NotValidPayload:
        await update.message.reply_text("❌ Please send valid text to translate.")
    except LanguageNotSupportedException:
        await update.message.reply_text("❌ Language not supported. Use /setlang to choose another.")
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(
            "❌ Translation failed. Please try again later."
        )

# ==================== BUTTON CALLBACK HANDLER ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button clicks"""
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()
    
    data = query.data
    
    if data == 'change_lang':
        # Show language selection
        current_lang = get_user_language(user_id)
        current_lang_name = get_language_name(current_lang)
        
        keyboard = []
        row = []
        for code, name in sorted(LANGUAGES.items()):
            display_name = f"✅ {name}" if code == current_lang else name
            row.append(InlineKeyboardButton(display_name, callback_data=f'lang_{code}'))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🌍 *Select Your Target Language*\n\nCurrent: *{current_lang_name}*",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    elif data == 'help':
        help_text = """
📖 *Available Commands*

/start - Welcome and setup
/help - Show this help menu
/setlang - Change target language
/languages - List all supported languages
/about - Bot information

💡 *Quick Guide:*
1. Set your target language with /setlang
2. Send any text message
3. I'll translate it instantly!

*Example:*
Send: "Hello, how are you?"
If target language is Spanish:
Reply: "Hola, ¿cómo estás?"

🔗 *Project:* Language39
"""
        await query.edit_message_text(help_text, parse_mode='Markdown')
        
    elif data == 'about':
        about_text = """
🤖 *Language39 Translator Bot*

*Version:* 1.0.0
*Developer:* Language39 Team
*Powered by:* Google Translate API

*Features:*
• Translate between 27+ languages
• Auto language detection
• User preferences saved
• Inline keyboard interface

*Project Website:* language39.com
*GitHub:* github.com/language39/translator-bot

Made with ❤️ for Language39 Project
"""
        await query.edit_message_text(about_text, parse_mode='Markdown')
        
    elif data == 'back_to_menu':
        current_lang = get_user_language(user_id)
        current_lang_name = get_language_name(current_lang)
        
        welcome_text = f"""
🤖 *Welcome to Language39 Translator Bot!*

I'm your personal translation assistant.

🌟 *Features:*
• Translate text to 27+ languages
• Auto-detect source language
• Save your language preference
• Simple and fast

📝 *How to use:*
• Send any text message to translate
• Use /setlang to change target language
• Use /help for all commands

🌍 *Your target language:* {current_lang_name}

Start translating now! 🚀
"""
        
        keyboard = [
            [InlineKeyboardButton("🌍 Change Language", callback_data='change_lang')],
            [InlineKeyboardButton("📖 Help", callback_data='help')],
            [InlineKeyboardButton("ℹ️ About", callback_data='about')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    elif data.startswith('lang_'):
        # Change user's language
        lang_code = data.replace('lang_', '')
        if lang_code in LANGUAGES:
            user_languages[user_id] = lang_code
            lang_name = get_language_name(lang_code)
            
            await query.edit_message_text(
                f"✅ Language changed to *{lang_name}* successfully!\n\n"
                f"Send me any text to translate to {lang_name}.",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("❌ Invalid language selection.")

# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Something went wrong. Please try again later."
        )

# ==================== MAIN FUNCTION ====================

def main():
    """Start the bot"""
    logger.info("🚀 Starting Language39 Translator Bot...")
    logger.info(f"Bot Token: {BOT_TOKEN[:10]}... (first 10 chars)")
    
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("setlang", setlang_command))
        application.add_handler(CommandHandler("languages", languages_command))
        application.add_handler(CommandHandler("about", about_command))
        
        # Add message handler (for text messages)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))
        
        # Add callback query handler (for inline buttons)
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Start the bot with polling
        logger.info("✅ Bot is running and ready to accept messages")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
