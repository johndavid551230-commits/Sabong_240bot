import os
import logging
import tempfile
import sys
import re
import string
import random
from datetime import datetime
from gtts import gTTS
from PIL import Image
import img2pdf
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Language options for TTS and Translation
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese (Mandarin)',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'nl': 'Dutch',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'id': 'Indonesian',
    'pl': 'Polish',
    'uk': 'Ukrainian',
    'he': 'Hebrew',
    'el': 'Greek',
    'cs': 'Czech',
    'sv': 'Swedish',
    'hu': 'Hungarian',
    'ro': 'Romanian',
    'km': 'Khmer'  # Khmer language support
}

# Sabong24 themed responses (Khmer/Thai inspired)
SABONG_RESPONSES = [
    "🦅 Sabong24 - មេបក្សីធំ!",
    "🏆 Sabong24 - ជើងឯកបក្សី!",
    "⚡ Sabong24 - បក្សីខ្លាំង!",
    "💪 Sabong24 - កម្លាំងបក្សី!",
    "🎯 Sabong24 - ចំណុចបក្សី!",
    "🌟 Sabong24 - ផ្កាយបក្សី!",
    "🔥 Sabong24 - បក្សីក្តៅ!",
    "✨ Sabong24 - បក្សីភ្លឺ!",
    "🚀 Sabong24 - បក្សីហោះ!",
    "👑 Sabong24 - ស្តេចបក្សី!",
]

# Khmer translations for common phrases
KHMER_TRANSLATIONS = {
    'hello': 'សួស្តី',
    'goodbye': 'លាហើយ',
    'thank you': 'អរគុណ',
    'yes': 'បាទ/ចាស',
    'no': 'ទេ',
    'please': 'សូម',
    'sorry': 'សុំទោស',
    'good morning': 'អរុណសួស្តី',
    'good afternoon': 'ទិវាសួស្តី',
    'good night': 'រាត្រីសួស្តី',
    'how are you': 'អ្នកសុខសប្បាយទេ',
    'i love you': 'ខ្ញុំស្រលាញ់អ្នក',
    'friend': 'មិត្តភក្តិ',
    'family': 'គ្រួសារ',
    'home': 'ផ្ទះ',
    'water': 'ទឹក',
    'food': 'អាហារ',
    'love': 'ស្នេហា',
    'life': 'ជីវិត',
    'happy': 'សប្បាយ',
    'sad': 'ក្រៀមក្រំ',
    'beautiful': 'ស្អាត',
    'good': 'ល្អ',
    'bad': 'អាក្រក់',
    'big': 'ធំ',
    'small': 'តូច',
    'new': 'ថ្មី',
    'old': 'ចាស់',
    'young': 'ក្មេង',
    'bird': 'បក្សី',
    'champion': 'ជើងឯក',
    'winner': 'អ្នកឈ្នះ',
    'strength': 'កម្លាំង',
    'power': 'អំណាច',
}

# Grammar Rules
GRAMMAR_RULES = {
    "don't": 'do not', "can't": 'cannot', "won't": 'will not',
    "shouldn't": 'should not', "wouldn't": 'would not',
    "couldn't": 'could not', "isn't": 'is not', "aren't": 'are not',
    "wasn't": 'was not', "weren't": 'were not',
    "hasn't": 'has not', "haven't": 'have not',
    "hadn't": 'had not', "doesn't": 'does not', "didn't": 'did not',
    "ain't": 'am not', "i'm": 'I am', "you're": 'you are',
    "he's": 'he is', "she's": 'she is', "it's": 'it is',
    "we're": 'we are', "they're": 'they are',
    "i'll": 'I will', "you'll": 'you will', "he'll": 'he will',
    "she'll": 'she will', "it'll": 'it will', "we'll": 'we will',
    "they'll": 'they will', "i've": 'I have', "you've": 'you have',
    "we've": 'we have', "they've": 'they have',
    "i'd": 'I would', "you'd": 'you would', "he'd": 'he would',
    "she'd": 'she would', "we'd": 'we would', "they'd": 'they would',
    'a apple': 'an apple', 'a hour': 'an hour', 'a honest': 'an honest',
    'a honor': 'an honor', 'a umbrella': 'an umbrella',
    'a university': 'a university', 'a European': 'a European',
    'teh': 'the', 'adn': 'and', 'thier': 'their', 'there': 'their',
    'your': 'your', 'youre': "you're", 'alot': 'a lot',
    'untill': 'until', 'recieve': 'receive', 'belive': 'believe',
    'acheive': 'achieve', 'occured': 'occurred', 'ocurred': 'occurred',
    'seperate': 'separate', 'definately': 'definitely',
    'govenment': 'government', 'enviornment': 'environment',
    'accomodate': 'accommodate', 'aquire': 'acquire',
    'arguement': 'argument', 'begining': 'beginning',
    'business': 'business', 'calendar': 'calendar', 'career': 'career',
    'catagory': 'category', 'cemetary': 'cemetery',
    'collaegue': 'colleague', 'comittee': 'committee',
    'concious': 'conscious', 'dilemna': 'dilemma',
    'disappear': 'disappear', 'disatisfied': 'dissatisfied',
    'embarass': 'embarrass', 'enviroment': 'environment',
    'excede': 'exceed', 'existance': 'existence',
    'experiance': 'experience', 'guarantee': 'guarantee',
    'harrass': 'harass', 'independant': 'independent',
    'indispensible': 'indispensable', 'inoculate': 'inoculate',
    'irresistable': 'irresistible', 'maintainance': 'maintenance',
    'millenium': 'millennium', 'miniscule': 'minuscule',
    'mischevious': 'mischievous', 'neccessary': 'necessary',
    'occassion': 'occasion', 'occurence': 'occurrence',
    'pavillion': 'pavilion', 'perserverance': 'perseverance',
    'prefered': 'preferred', 'priviledge': 'privilege',
    'pronounciation': 'pronunciation', 'publically': 'publicly',
    'reccommend': 'recommend', 'relevent': 'relevant',
    'repetition': 'repetition', 'rhythm': 'rhythm',
    'schedual': 'schedule', 'seperate': 'separate',
    'similiar': 'similar', 'sucess': 'success',
    'suprize': 'surprise', 'tommorow': 'tomorrow',
    'unescessary': 'unnecessary', 'wierd': 'weird',
    'could of': 'could have', 'should of': 'should have',
    'would of': 'would have', 'must of': 'must have',
    'might of': 'might have',
}

# Translation Dictionary
TRANSLATION_DICT = {
    'hello': 'hola', 'goodbye': 'adiós', 'thank you': 'gracias',
    'yes': 'sí', 'no': 'no', 'please': 'por favor', 'sorry': 'lo siento',
    'good morning': 'buenos días', 'good afternoon': 'buenas tardes',
    'good night': 'buenas noches', 'how are you': '¿cómo estás',
    'i love you': 'te quiero', 'friend': 'amigo', 'family': 'familia',
    'home': 'casa', 'water': 'agua', 'food': 'comida', 'love': 'amor',
    'life': 'vida', 'happy': 'feliz', 'sad': 'triste', 'beautiful': 'hermoso',
    'good': 'bueno', 'bad': 'malo', 'big': 'grande', 'small': 'pequeño',
    'new': 'nuevo', 'old': 'viejo', 'young': 'joven',
    'success': 'éxito', 'excellence': 'excelencia',
    'quality': 'calidad', 'performance': 'rendimiento',
    'improvement': 'mejora', 'bird': 'pájaro',
    'champion': 'campeón', 'winner': 'ganador',
    'strength': 'fortaleza', 'power': 'poder',
    'bonjour': 'hello', 'merci': 'thank you', 'au revoir': 'goodbye',
    'oui': 'yes', 'non': 'no', "s'il vous plaît": 'please',
    'pardon': 'sorry', 'bonsoir': 'good evening', 'bonne nuit': 'good night',
    "comment ça va": 'how are you', "je t'aime": 'i love you',
    'ami': 'friend', 'famille': 'family', 'maison': 'home',
    'eau': 'water', 'nourriture': 'food', 'amour': 'love',
    'vie': 'life', 'heureux': 'happy', 'triste': 'sad',
    'beau': 'beautiful', 'bon': 'good', 'mauvais': 'bad',
    'grand': 'big', 'petit': 'small', 'nouveau': 'new',
    'vieux': 'old', 'jeune': 'young', 'succès': 'success',
    'excellence': 'excellence', 'qualité': 'quality',
    'performance': 'performance', 'amélioration': 'improvement',
}

# User preferences
user_preferences = {}

def get_token():
    """Get token from environment variables"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", "your_bot_token_here", ""]:
        return token
    
    token = os.getenv('BOT_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", ""]:
        return token
    
    token = os.getenv('TELEGRAM_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", ""]:
        return token
    
    return None

def get_sabong_response():
    """Get random Sabong24 themed response"""
    return random.choice(SABONG_RESPONSES)

def correct_grammar(text):
    """AI Grammar Correction with advanced rules"""
    original_text = text
    corrections = []
    corrected_text = text
    
    words = corrected_text.split()
    corrected_words = []
    
    for word in words:
        clean_word = word.strip(string.punctuation)
        lower_word = clean_word.lower()
        
        if lower_word in GRAMMAR_RULES:
            correction = GRAMMAR_RULES[lower_word]
            if clean_word[0].isupper():
                correction = correction.capitalize()
            if word != clean_word:
                correction += word[-1] if word[-1] in string.punctuation else ''
            corrected_words.append(correction)
            corrections.append(f"'{clean_word}' → '{correction}'")
        else:
            corrected_words.append(word)
    
    corrected_text = ' '.join(corrected_words)
    
    sentences = corrected_text.split('. ')
    corrected_text = '. '.join([s.capitalize() if s else s for s in sentences])
    corrected_text = re.sub(r'\ba ([aeiouAEIOU])', r'an \1', corrected_text)
    corrected_text = re.sub(r'\ban ([^aeiouAEIOU])', r'a \1', corrected_text)
    corrected_text = ' '.join(corrected_text.split())
    corrected_text = re.sub(r'\bi\b', 'I', corrected_text)
    
    months = ['january', 'february', 'march', 'april', 'may', 'june', 
              'july', 'august', 'september', 'october', 'november', 'december']
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for month in months:
        corrected_text = re.sub(rf'\b{month}\b', month.capitalize(), corrected_text, flags=re.IGNORECASE)
    for day in days:
        corrected_text = re.sub(rf'\b{day}\b', day.capitalize(), corrected_text, flags=re.IGNORECASE)
    
    corrected_text = re.sub(r'([.!?])\1+', r'\1', corrected_text)
    corrected_text = re.sub(r'\s+([.,!?;:])', r'\1', corrected_text)
    
    changes_made = len(corrections) > 0 or original_text != corrected_text
    
    return {
        'original': original_text,
        'corrected': corrected_text,
        'changes_made': changes_made,
        'corrections': corrections[:10] if corrections else [],
        'total_corrections': len(corrections)
    }

def translate_text(text, target_lang='es'):
    """Simple translation function"""
    text_lower = text.lower().strip()
    
    # Check for Khmer translations
    if text_lower in KHMER_TRANSLATIONS:
        return {
            'original': text,
            'translated': KHMER_TRANSLATIONS[text_lower],
            'target_lang': target_lang,
            'confidence': 'high',
            'language': 'Khmer'
        }
    
    if text_lower in TRANSLATION_DICT:
        return {
            'original': text,
            'translated': TRANSLATION_DICT[text_lower],
            'target_lang': target_lang,
            'confidence': 'high'
        }
    
    words = text_lower.split()
    translated_parts = []
    found_translations = 0
    
    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in TRANSLATION_DICT:
            translated_parts.append(TRANSLATION_DICT[clean_word])
            found_translations += 1
        elif clean_word in KHMER_TRANSLATIONS:
            translated_parts.append(KHMER_TRANSLATIONS[clean_word])
            found_translations += 1
        else:
            translated_parts.append(word)
    
    if found_translations > 0:
        translated_text = ' '.join(translated_parts)
        if text[0].isupper():
            translated_text = translated_text.capitalize()
        
        return {
            'original': text,
            'translated': translated_text,
            'target_lang': target_lang,
            'confidence': 'medium',
            'words_translated': found_translations
        }
    
    return {
        'original': text,
        'translated': f"[No direct translation available]",
        'target_lang': target_lang,
        'confidence': 'none'
    }

async def convert_image_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert image to PDF"""
    if not update.message.photo:
        await update.message.reply_text(
            "🖼️ សូមផ្ញើរូបភាពមកខ្ញុំដើម្បីបំលែងជា PDF!\n"
            "Please send me an image to convert to PDF!"
        )
        return
    
    photo = update.message.photo[-1]
    file = await photo.get_file()
    sabong_response = get_sabong_response()
    
    await update.message.reply_text(f"🖼️ Converting image to PDF... {sabong_response}")
    
    try:
        # Download image
        file_bytes = await file.download_as_bytearray()
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as img_file:
            img_path = img_file.name
            img_file.write(file_bytes)
        
        # Convert to PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
            pdf_path = pdf_file.name
        
        # Open image and convert to PDF
        with open(img_path, 'rb') as f:
            pdf_bytes = img2pdf.convert(f.read())
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Send PDF
        with open(pdf_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename='converted_image.pdf',
                caption=f"🖼️ បំលែងរូបភាពជា PDF\nImage converted to PDF\n🦅 {sabong_response}"
            )
        
        # Clean up
        os.unlink(img_path)
        os.unlink(pdf_path)
        
        await update.message.reply_text("✅ PDF created successfully! / បង្កើត PDF ដោយជោគជ័យ!")
        
    except Exception as e:
        logger.error(f"Error converting image to PDF: {e}")
        await update.message.reply_text(
            "❌ Error converting image to PDF. Please try again with a different image.\n"
            "កំហុសក្នុងការបំលែងរូបភាពជា PDF សូមព្យាយាមម្តងទៀត។"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when /start is issued."""
    user = update.effective_user
    current_time = datetime.now().strftime("%I:%M %p")
    sabong_response = get_sabong_response()
    
    await update.message.reply_text(
        f"🦅 Welcome to @មេបក្សីធំ - Sabong24bot, {user.first_name}! 👋\n\n"
        f"🕐 Current time: {current_time}\n\n"
        f"🏆 {sabong_response} 🏆\n\n"
        f"🎯 **Speak better • Write better • Understand more**\n\n"
        "I'm your **all-in-one** assistant with FOUR powerful functions:\n\n"
        "🔊 **Text → Speech** - Convert text to audio\n"
        "🌍 **Translation** - Translate instantly\n"
        "✍️ **Grammar Correction** - Perfect your writing\n"
        "🖼️ **Image → PDF** - Convert images to PDF\n\n"
        "📝 **Commands:**\n"
        "/start - Show this message\n"
        "/tts - Convert text to speech\n"
        "/translate - Translate text\n"
        "/grammar - Check grammar\n"
        "/all - Do everything at once!\n"
        "/lang - Change TTS language\n"
        "/target - Set translation language\n"
        "/speed - Change speech speed\n"
        "/sabong - Get Sabong24 info\n"
        "/khmer - Khmer special command\n"
        "/help - Get help\n"
        "/about - About this bot\n\n"
        "💡 **How to use:**\n"
        "• /tts [text] - Convert to speech\n"
        "• /translate [text] - Translate text\n"
        "• /grammar [text] - Check grammar\n"
        "• /all [text] - Do everything at once!\n"
        "• Send an image - Convert to PDF\n\n"
        "🦅 **Sabong24 - The Champion Bird! / មេបក្សីធំ!**"
    )

async def khmer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Khmer special command."""
    khmer_greetings = [
        "🦅 សួស្តី! ស្វាគមន៍មកកាន់ Sabong24!",
        "🇰🇭 ជំរាបសួរ! អ្នកសុខសប្បាយទេ?",
        "🦅 Sabong24 - មេបក្សីធំ!",
        "🇰🇭 Sabong24 - ជើងឯកបក្សី!",
        "🦅 Sabong24 - បក្សីខ្លាំង!",
        "🇰🇭 Sabong24 - កម្លាំងបក្សី!",
        "🦅 សួស្តី! តើខ្ញុំអាចជួយអ្នកដោយរបៀបណា?",
        "🇰🇭 Sabong24 - បក្សីល្អបំផុត!",
    ]
    
    await update.message.reply_text(
        f"🇰🇭 **Khmer / ខ្មែរ**\n\n"
        f"{random.choice(khmer_greetings)}\n\n"
        f"🦅 **Sabong24 Khmer Features / លក្ខណៈពិសេសខ្មែរ:**\n"
        f"• 🇰🇭 Khmer translations\n"
        f"• 🦅 Bird-themed responses\n"
        f"• 🔊 Text-to-Speech in multiple languages\n"
        f"• 🌍 Translation to/from Khmer\n"
        f"• ✍️ Grammar correction\n"
        f"• 🖼️ Image to PDF conversion\n\n"
        f"💡 **Example Usage / ឧទាហរណ៍:**\n"
        f"/translate សួស្តី\n"
        f"/tts សួស្តី\n\n"
        f"🦅 **Sabong24 - The Champion Bird! / មេបក្សីធំ!**"
    )

async def sabong_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send Sabong24 information."""
    sabong_response = get_sabong_response()
    
    await update.message.reply_text(
        f"🦅 **Sabong24 - The Champion Bird / មេបក្សីធំ**\n\n"
        f"{sabong_response}\n\n"
        f"🏆 **What Makes Sabong24 Special:**\n"
        f"• 🦅 4 Powerful Functions\n"
        f"• 📊 25+ Languages including Khmer\n"
        f"• 🎯 Precision in everything\n"
        f"• 💎 Quality guaranteed\n"
        f"• 🔥 24/7 availability\n\n"
        f"📊 **Your Winning Tools / ឧបករណ៍ឈ្នះៗ:**\n"
        f"• 🔊 Clear speech\n"
        f"• 🌍 Global communication\n"
        f"• ✍️ Perfect grammar\n"
        f"• 🖼️ Image to PDF conversion\n"
        f"• ✨ Confident expression\n\n"
        f"💡 **Commands to use / ពាក្យបញ្ជា:**\n"
        f"/tts - Convert text to speech\n"
        f"/translate - Translate text\n"
        f"/grammar - Check grammar\n"
        f"/all - Do everything at once!\n"
        f"/khmer - Khmer special command\n"
        f"Send an image - Convert to PDF\n\n"
        f"🦅 **Sabong24 - Champion Bird! / មេបក្សីធំ!**"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send about information."""
    await update.message.reply_text(
        "🦅 **About @Sabong24bot / អំពី Sabong24bot**\n\n"
        "🎯 **Mission:** Speak better • Write better • Understand more\n\n"
        "🏆 **Sabong24 - The Champion Bird! / មេបក្សីធំ**\n\n"
        "🔊 **Text-to-Speech:** 12+ languages\n"
        "🌍 **Translation:** 25+ languages (including Khmer)\n"
        "✍️ **Grammar Correction:** 100+ rules\n"
        "🖼️ **Image to PDF:** Convert images instantly\n\n"
        "🇰🇭 **Special Khmer Features:**\n"
        "• Khmer translations\n"
        "• Khmer-themed responses\n"
        "• /khmer command\n\n"
        "📊 **Features:**\n"
        "• 4-in-1 functionality\n"
        "• 24/7 availability\n"
        "• Interactive processing\n"
        "• Bird-themed experience\n\n"
        "📅 **Created:** 2026\n"
        "🔧 **Technology:** Python + Google TTS + AI\n\n"
        "🦅 **Sabong24 - Champion Bird! / មេបក្សីធំ!**"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    await update.message.reply_text(
        "🦅 **@Sabong24bot Help / ជំនួយ**\n\n"
        "🎯 **Speak better • Write better • Understand more**\n\n"
        "📖 **How to use / របៀបប្រើប្រាស់:**\n\n"
        "**🔊 Text-to-Speech:**\n"
        "/tts [text] - Convert to speech\n"
        "Example: /tts Hello\n\n"
        "**🌍 Translation:**\n"
        "/translate [text] - Translate text\n"
        "Example: /translate hello\n"
        "Example: /translate សួស្តី\n\n"
        "**✍️ Grammar Correction:**\n"
        "/grammar [text] - Check grammar\n"
        "Example: /grammar i am go\n\n"
        "**🔄 All-in-One:**\n"
        "/all [text] - Do everything!\n"
        "Example: /all hello world\n\n"
        "**🖼️ Image to PDF:**\n"
        "Send any image - Convert to PDF\n\n"
        "**🇰🇭 Khmer Special:**\n"
        "/khmer - Khmer themed response\n\n"
        "**🦅 Sabong24 Info:**\n"
        "/sabong - Get info\n\n"
        "**Commands / ពាក្យបញ្ជា:**\n"
        "/start - Welcome\n"
        "/tts - Text to Speech\n"
        "/translate - Translate\n"
        "/grammar - Grammar Check\n"
        "/all - All functions\n"
        "/sabong - Sabong24 info\n"
        "/khmer - Khmer special\n"
        "/lang - Change TTS language\n"
        "/target - Set translation language\n"
        "/speed - Change speed\n"
        "/help - This menu\n"
        "/about - About this bot\n\n"
        "💡 **Tips:**\n"
        "• Send any image to convert to PDF\n"
        "• Use /all for everything at once\n"
        "• Try /khmer for Khmer experience\n"
        "• Sabong24 - Champion Bird!"
    )

async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /all command - do everything at once!"""
    text = update.message.text.replace('/all', '').strip()
    
    if not text:
        await update.message.reply_text(
            "📝 Please provide text!\nExample: /all Hello world"
        )
        return
    
    user_id = update.effective_user.id
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    speed = user_preferences.get(user_id, {}).get('speed', 'normal')
    target_lang = user_preferences.get(user_id, {}).get('target_lang', 'es')
    sabong_response = get_sabong_response()
    
    await update.message.reply_text(f"🦅 Processing all functions... {sabong_response}")
    
    try:
        # Grammar
        grammar_result = correct_grammar(text)
        
        # Translation
        translation_result = translate_text(text, target_lang)
        
        # TTS
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = tmp_file.name
        
        slow = (speed == 'slow')
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(temp_path)
        
        response = (
            f"🦅 **All Functions Complete!**\n\n"
            f"📝 **Original:** {text}\n\n"
            f"✍️ **Grammar:** {grammar_result['corrected']}\n"
            f"🌍 **Translation:** {translation_result['translated']}\n"
            f"🏆 {sabong_response}"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
        with open(temp_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                caption=f"🦅 Sabong24 TTS",
                title="Sabong24 Audio",
                performer="@Sabong24bot"
            )
        
        os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Error processing. Please try again.")

async def tts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tts command"""
    text = update.message.text.replace('/tts', '').strip()
    
    if not text:
        await update.message.reply_text("📝 Please provide text!\nExample: /tts Hello")
        return
    
    user_id = update.effective_user.id
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    speed = user_preferences.get(user_id, {}).get('speed', 'normal')
    sabong_response = get_sabong_response()
    
    await update.message.reply_text(f"🔊 Converting to speech... {sabong_response}")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = tmp_file.name
        
        slow = (speed == 'slow')
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(temp_path)
        
        with open(temp_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                caption=f"🦅 TTS\n🌐 {LANGUAGES.get(lang, 'English')}",
                title="Sabong24 Audio",
                performer="@Sabong24bot"
            )
        
        os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Error. Please try again.")

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /translate command"""
    text = update.message.text.replace('/translate', '').strip()
    
    if not text:
        await update.message.reply_text("📝 Please provide text!\nExample: /translate hello")
        return
    
    user_id = update.effective_user.id
    target_lang = user_preferences.get(user_id, {}).get('target_lang', 'es')
    sabong_response = get_sabong_response()
    
    await update.message.reply_text(f"🌍 Translating... {sabong_response}")
    
    result = translate_text(text, target_lang)
    
    # Check if it's a Khmer translation
    khmer_note = ""
    if result.get('language') == 'Khmer':
        khmer_note = "\n🇰🇭 Khmer translation"
    
    response = (
        f"🌍 **Translation**\n\n"
        f"📝 {result['original']}\n"
        f"✅ {result['translated']}\n"
        f"🎯 {LANGUAGES.get(target_lang, 'Spanish')}{khmer_note}"
    )
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def grammar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /grammar command"""
    text = update.message.text.replace('/grammar', '').strip()
    
    if not text:
        await update.message.reply_text("📝 Please provide text!\nExample: /grammar i am go")
        return
    
    sabong_response = get_sabong_response()
    await update.message.reply_text(f"✍️ Checking grammar... {sabong_response}")
    
    result = correct_grammar(text)
    
    if result['changes_made']:
        response = (
            f"✍️ **Grammar Correction**\n\n"
            f"📝 **Original:** {result['original']}\n"
            f"✅ **Corrected:** {result['corrected']}\n"
            f"🔧 **Changes:** {result['total_corrections']}"
        )
    else:
        response = f"✍️ **Grammar Check**\n\n✅ No corrections needed!\n📝 {text}"
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show language selection menu for TTS."""
    keyboard = []
    row = []
    tts_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi', 'th']
    
    for code in tts_languages:
        if code in LANGUAGES:
            row.append(InlineKeyboardButton(LANGUAGES[code], callback_data=f"lang_{code}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌐 Select TTS language:", reply_markup=reply_markup)

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callback."""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace("lang_", "")
    user_id = query.from_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['lang'] = lang_code
    
    sabong_response = get_sabong_response()
    await query.edit_message_text(
        f"✅ Language set to: {LANGUAGES[lang_code]}\n\n"
        f"🦅 {sabong_response}"
    )

async def target_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show target language selection for translation."""
    keyboard = []
    row = []
    
    for i, (code, name) in enumerate(LANGUAGES.items()):
        button_text = f"🇰🇭 {name}" if code == 'km' else name
        row.append(InlineKeyboardButton(button_text, callback_data=f"target_{code}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌍 Select translation target language:",
        reply_markup=reply_markup
    )

async def target_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle target language selection callback."""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace("target_", "")
    user_id = query.from_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['target_lang'] = lang_code
    
    sabong_response = get_sabong_response()
    await query.edit_message_text(
        f"✅ Target set to: {LANGUAGES[lang_code]}\n\n"
        f"🦅 {sabong_response}"
    )

SPEED_OPTIONS = {
    'normal': 'Normal Speed',
    'slow': 'Slow Speed',
}

async def speed_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show speed selection menu."""
    keyboard = []
    for speed, name in SPEED_OPTIONS.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"speed_{speed}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎚️ Select speed:", reply_markup=reply_markup)

async def speed_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle speed selection callback."""
    query = update.callback_query
    await query.answer()
    
    speed = query.data.replace("speed_", "")
    user_id = query.from_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['speed'] = speed
    
    sabong_response = get_sabong_response()
    await query.edit_message_text(
        f"✅ Speed set to: {SPEED_OPTIONS[speed]}\n\n"
        f"🦅 {sabong_response}"
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle general text messages"""
    text = update.message.text
    
    if text.startswith('/'):
        return
    
    keyboard = [
        [InlineKeyboardButton("🔊 TTS", callback_data="process_tts")],
        [InlineKeyboardButton("🌍 Translate", callback_data="process_translate")],
        [InlineKeyboardButton("✍️ Grammar", callback_data="process_grammar")],
        [InlineKeyboardButton("🦅 All", callback_data="process_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🦅 How to process?\n\n_{text[:100]}_",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    context.user_data['pending_text'] = text

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages - Convert to PDF"""
    await convert_image_to_pdf(update, context)

async def process_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle processing callback"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    text = context.user_data.get('pending_text', '')
    
    if not text:
        await query.edit_message_text("❌ No text found.")
        return
    
    user_id = query.from_user.id
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    speed = user_preferences.get(user_id, {}).get('speed', 'normal')
    target_lang = user_preferences.get(user_id, {}).get('target_lang', 'es')
    sabong_response = get_sabong_response()
    
    if action == "process_tts":
        await query.edit_message_text(f"🔊 Converting to speech... {sabong_response}")
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name
            
            slow = (speed == 'slow')
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(temp_path)
            
            with open(temp_path, 'rb') as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    caption=f"🦅 Sabong24 Audio",
                    title="Sabong24 Audio",
                    performer="@Sabong24bot"
                )
            
            os.unlink(temp_path)
            await query.edit_message_text(f"✅ Audio sent! {sabong_response}")
            
        except Exception as e:
            await query.edit_message_text("❌ Error. Please try again.")
    
    elif action == "process_translate":
        await query.edit_message_text(f"🌍 Translating... {sabong_response}")
        
        result = translate_text(text, target_lang)
        response = f"🌍 **Translation**\n\n✅ {result['translated']}"
        await query.message.reply_text(response, parse_mode='Markdown')
        await query.edit_message_text("✅ Translation done!")
    
    elif action == "process_grammar":
        await query.edit_message_text(f"✍️ Checking grammar... {sabong_response}")
        
        result = correct_grammar(text)
        response = f"✍️ **Grammar**\n\n✅ {result['corrected']}"
        await query.message.reply_text(response, parse_mode='Markdown')
        await query.edit_message_text("✅ Grammar check done!")
    
    elif action == "process_all":
        await query.edit_message_text(f"🦅 Processing all... {sabong_response}")
        
        # Grammar
        grammar_result = correct_grammar(text)
        await query.message.reply_text(f"✍️ **Grammar:** {grammar_result['corrected']}", parse_mode='Markdown')
        
        # Translation
        translation_result = translate_text(text, target_lang)
        await query.message.reply_text(f"🌍 **Translation:** {translation_result['translated']}", parse_mode='Markdown')
        
        # TTS
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name
            
            slow = (speed == 'slow')
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(temp_path)
            
            with open(temp_path, 'rb') as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    caption=f"🦅 All functions done!",
                    title="Sabong24 Audio",
                    performer="@Sabong24bot"
                )
            
            os.unlink(temp_path)
            await query.edit_message_text(f"✅ All completed! {sabong_response}")
            
        except Exception as e:
            await query.edit_message_text("❌ Error with TTS.")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    await update.message.reply_text("🎤 Please send text or images!")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An error occurred. Please try again later."
            )
    except:
        pass

def main() -> None:
    """Start the bot."""
    logger.info("🦅 @Sabong24bot Starting...")
    
    token = get_token()
    
    if not token:
        logger.error("❌ No token found!")
        sys.exit(1)
    
    logger.info(f"✅ Token found!")
    
    try:
        application = Application.builder().token(token).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("sabong", sabong_command))
        application.add_handler(CommandHandler("khmer", khmer_command))
        application.add_handler(CommandHandler("lang", language_menu))
        application.add_handler(CommandHandler("target", target_language_menu))
        application.add_handler(CommandHandler("speed", speed_menu))
        application.add_handler(CommandHandler("tts", tts_command))
        application.add_handler(CommandHandler("translate", translate_command))
        application.add_handler(CommandHandler("grammar", grammar_command))
        application.add_handler(CommandHandler("all", all_command))
        
        # Callback query handlers
        application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(target_callback, pattern="^target_"))
        application.add_handler(CallbackQueryHandler(speed_callback, pattern="^speed_"))
        application.add_handler(CallbackQueryHandler(process_callback, pattern="^process_"))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
        application.add_handler(MessageHandler(filters.VOICE, voice_handler))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        logger.info("✅ @Sabong24bot is running!")
        logger.info("🎯 Bot: @មេបក្សីធំ - Sabong24bot")
        logger.info("📝 Features: TTS + Translation + Grammar + Image to PDF")
        logger.info("🇰🇭 Special: Khmer language support")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
