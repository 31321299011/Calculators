# ==================================================
# 🔥 SUPER ULTRA CALCULATOR BOT v4.0.0
# 🌐 Multi-Language: বাংলা | English | Русский | हिन्दी
# 👨‍💻 Developers: @bot_Developer_io & @jhgmaing
# ==================================================

import logging
import re
import math
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============ ⚙️ CONFIG ============
BOT_TOKEN = "8691010655:AAHXVL-CqUd-PKkF2NDHr9jS2u0bJQAEDAc"
ADMIN_IDS = [8194390770, 7134813314]
DB_NAME = "bot_data.db"
VERSION = "4.0.0"
DEVELOPERS = "@bot_Developer_io & @jhgmaing"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============ 🌍 LANGUAGE SYSTEM ============
LANG = {
    "bn": {
        "start_user": "👋 হ্যালো! আমি স্মার্ট ক্যালকুলেটর বট।\n\n"
                      "📌 আমাকে আপনার গ্রুপে অ্যাড করুন। গ্রুপে যেকোনো অঙ্ক (যেমন: 2+2*5, sqrt(81), pi*2) লিখলেই সাথে সাথে উত্তর দেব।\n\n"
                      "🌐 সংস্করণ: {version}\n"
                      "👨‍💻 ডেভেলপার: {dev}",
        "start_admin": "👑 অ্যাডমিন প্যানেল\n\n🌐 সংস্করণ: {version}\n👨‍💻 {dev}",
        "help": "🧠 ক্যালকুলেটর ব্যবহার:\n"
                "• সরাসরি অঙ্ক লিখুন: 2+3*4\n"
                "• ফাংশন: sqrt(144), sin(30), log(100), pi*2\n"
                "• গ্রুপে স্বয়ংক্রিয়ভাবে উত্তর দেয়।",
        "credits": "👨‍💻 ডেভেলপার: {dev}\n🌐 সংস্করণ: {version}",
        "not_math": "🙏 দয়া করে যেকোনো অঙ্ক লিখুন (যেমন: `2+3*4`, `sqrt(100)`)",
        "calc_result": "🧮 {result}",
        "all_users": "👥 মোট চ্যাট: {count}",
        "broadcast_prompt": "📢 যা পাঠাতে চান (টেক্সট/ছবি/ভিডিও) সেন্ড করুন। বাতিল করতে /cancel",
        "broadcast_done": "✅ ব্রডকাস্ট শেষ!\nসফল: {success}\nব্যর্থ: {fail}",
        "broadcast_cancel": "❌ ব্রডকাস্ট বাতিল।",
    },
    "en": {
        "start_user": "👋 Hello! I am Smart Calculator Bot.\n\n"
                      "📌 Add me to your group. I'll automatically solve any math expression like 2+2*5, sqrt(81), pi*2.\n\n"
                      "🌐 Version: {version}\n"
                      "👨‍💻 Developers: {dev}",
        "start_admin": "👑 Admin Panel\n\n🌐 Version: {version}\n👨‍💻 {dev}",
        "help": "🧠 Usage:\n"
                "• Direct math: 2+3*4\n"
                "• Functions: sqrt(144), sin(30), log(100), pi*2\n"
                "• Automatically answers in groups.",
        "credits": "👨‍💻 Developers: {dev}\n🌐 Version: {version}",
        "not_math": "🙏 Please send a math expression (e.g. `2+3*4`, `sqrt(100)`)",
        "calc_result": "🧮 {result}",
        "all_users": "👥 Total chats: {count}",
        "broadcast_prompt": "📢 Send what you want to broadcast (text/photo/video). Cancel with /cancel",
        "broadcast_done": "✅ Broadcast finished!\nSuccess: {success}\nFailed: {fail}",
        "broadcast_cancel": "❌ Broadcast cancelled.",
    },
    "ru": {
        "start_user": "👋 Привет! Я умный бот-калькулятор.\n\n"
                      "📌 Добавьте меня в группу. Я автоматически решаю примеры: 2+2*5, sqrt(81), pi*2.\n\n"
                      "🌐 Версия: {version}\n"
                      "👨‍💻 Разработчики: {dev}",
        "start_admin": "👑 Админ-панель\n\n🌐 Версия: {version}\n👨‍💻 {dev}",
        "help": "🧠 Использование:\n"
                "• Введите пример: 2+3*4\n"
                "• Функции: sqrt(144), sin(30), log(100), pi*2\n"
                "• В группах отвечает автоматически.",
        "credits": "👨‍💻 Разработчики: {dev}\n🌐 Версия: {version}",
        "not_math": "🙏 Пожалуйста, отправьте математическое выражение (напр. `2+3*4`, `sqrt(100)`)",
        "calc_result": "🧮 {result}",
        "all_users": "👥 Всего чатов: {count}",
        "broadcast_prompt": "📢 Отправьте контент для рассылки (текст/фото/видео). Отмена /cancel",
        "broadcast_done": "✅ Рассылка завершена!\nУспешно: {success}\nНеудачно: {fail}",
        "broadcast_cancel": "❌ Рассылка отменена.",
    },
    "hi": {
        "start_user": "👋 नमस्ते! मैं स्मार्ट कैलकुलेटर बॉट हूँ।\n\n"
                      "📌 मुझे अपने ग्रुप में जोड़ें। मैं 2+2*5, sqrt(81), pi*2 जैसे सवाल खुद हल करूंगा।\n\n"
                      "🌐 संस्करण: {version}\n"
                      "👨‍💻 डेवलपर: {dev}",
        "start_admin": "👑 एडमिन पैनल\n\n🌐 संस्करण: {version}\n👨‍💻 {dev}",
        "help": "🧠 उपयोग:\n"
                "• सीधा गणित: 2+3*4\n"
                "• फंक्शन: sqrt(144), sin(30), log(100), pi*2\n"
                "• ग्रुप में अपने आप जवाब देता है।",
        "credits": "👨‍💻 डेवलपर: {dev}\n🌐 संस्करण: {version}",
        "not_math": "🙏 कृपया कोई गणित अभिव्यक्ति भेजें (जैसे `2+3*4`, `sqrt(100)`)",
        "calc_result": "🧮 {result}",
        "all_users": "👥 कुल चैट: {count}",
        "broadcast_prompt": "📢 प्रसारण सामग्री भेजें (टेक्स्ट/फोटो/वीडियो)। रद्द करें /cancel",
        "broadcast_done": "✅ प्रसारण समाप्त!\nसफल: {success}\nअसफल: {fail}",
        "broadcast_cancel": "❌ प्रसारण रद्द।",
    }
}

def get_lang(user) -> dict:
    code = user.language_code or "en"
    if code.startswith("bn"):
        return LANG["bn"]
    elif code.startswith("ru"):
        return LANG["ru"]
    elif code.startswith("hi"):
        return LANG["hi"]
    else:
        return LANG["en"]

# ============ 🗄️ DATABASE ============
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                type TEXT NOT NULL
            )
        """)
        conn.commit()
init_db()

def save_chat(chat_id, chat_type):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR IGNORE INTO users (chat_id, type) VALUES (?, ?)", (chat_id, chat_type))
        conn.commit()

def get_all_chats():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT chat_id, type FROM users").fetchall()

def get_user_count():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

# ============ 🧮 SAFE MATH ENGINE ============
ALLOWED_NAMES = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
ALLOWED_NAMES.update({
    "abs": abs, "round": round, "min": min, "max": max, "pow": pow,
    "int": int, "float": float, "pi": math.pi, "e": math.e,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "log": math.log, "log10": math.log10, "sqrt": math.sqrt,
    "ceil": math.ceil, "floor": math.floor, "factorial": math.factorial,
    "degrees": math.degrees, "radians": math.radians,
})

def safe_eval(expr: str):
    expr = expr.replace("^", "**")
    code = compile(expr, "<string>", "eval")
    for name in code.co_names:
        if name not in ALLOWED_NAMES:
            raise NameError(f"'{name}' not allowed")
    return eval(code, {"__builtins__": {}}, ALLOWED_NAMES)

def extract_calc(text: str):
    text = text.strip()
    if not text:
        return None

    # 1. পুরো টেক্সট এক্সপ্রেশন কিনা চেক
    if re.match(r'^[0-9+\-*/%^().\s\wπe]+$', text):
        try:
            return format_result(safe_eval(text))
        except Exception:
            pass

    # 2. ভিতর থেকে এক্সপ্রেশন খোঁজা
    patterns = [
        r'([-+]?\d*\.?\d+[+\-*/%^]+[-+]?\d*\.?\d+(?:[+\-*/%^][-+]?\d*\.?\d+)*)',
        r'((?:sqrt|sin|cos|tan|log|pi|e|abs|factorial|pow)\s*\([^)]+\))',
        r'([-+]?\d*\.?\d+\s*[+\-*/%^]\s*[-+]?\d*\.?\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            expr = match.group(1).strip()
            try:
                return format_result(safe_eval(expr))
            except Exception:
                continue
    return None

def format_result(res):
    if isinstance(res, float):
        return f"{res:.10f}".rstrip('0').rstrip('.')
    return str(res)

# ============ 📢 BROADCAST STATE ============
BROADCAST_STATE = 1

# ============ 🚀 HANDLERS ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    lang = get_lang(user)

    if chat.type == "private":
        save_chat(chat.id, "private")
        if user.id in ADMIN_IDS:
            keyboard = [["📊 All Users", "📢 Broadcast"]]
            await update.message.reply_text(
                lang["start_admin"].format(version=VERSION, dev=DEVELOPERS),
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
        else:
            await update.message.reply_text(
                lang["start_user"].format(version=VERSION, dev=DEVELOPERS)
            )
    else:
        # গ্রুপ – চুপচাপ চ্যাট আইডি সেভ
        save_chat(chat.id, "group")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user)
    await update.message.reply_text(lang["help"])

async def credits_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user)
    await update.message.reply_text(lang["credits"].format(dev=DEVELOPERS, version=VERSION))

async def new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ When bot is added to a group – stay completely silent """
    chat = update.effective_chat
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            save_chat(chat.id, "group")
            break

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user
    chat = update.effective_chat
    text = msg.text.strip() if msg.text else ""
    lang = get_lang(user)

    save_chat(chat.id, "private" if chat.type == "private" else "group")

    # ===== ADMIN PRIVATE BROADCAST FLOW =====
    if user.id in ADMIN_IDS and chat.type == "private":
        state = context.user_data.get("state")
        if state == BROADCAST_STATE:
            await broadcast_content(update, context)
            context.user_data["state"] = None
            return
        if text == "📊 All Users":
            await msg.reply_text(lang["all_users"].format(count=get_user_count()))
            return
        if text == "📢 Broadcast":
            context.user_data["state"] = BROADCAST_STATE
            await msg.reply_text(lang["broadcast_prompt"])
            return
        if text == "/cancel":
            context.user_data["state"] = None
            await msg.reply_text(lang["broadcast_cancel"])
            return

    # ===== AUTO CALCULATOR (group + non‑admin private) =====
    if chat.type == "group" or (chat.type == "private" and user.id not in ADMIN_IDS):
        if not (user.id in ADMIN_IDS and context.user_data.get("state") == BROADCAST_STATE):
            result = extract_calc(text)
            if result:
                await msg.reply_text(lang["calc_result"].format(result=result))
            elif chat.type == "private":
                await msg.reply_text(lang["not_math"])

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user
    chat = update.effective_chat
    save_chat(chat.id, "private" if chat.type == "private" else "group")

    if user.id in ADMIN_IDS and chat.type == "private" and context.user_data.get("state") == BROADCAST_STATE:
        await broadcast_content(update, context)
        context.user_data["state"] = None

async def broadcast_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    lang = get_lang(update.effective_user)
    chats = get_all_chats()
    success = fail = 0
    for cid, _ in chats:
        try:
            if msg.text:
                await context.bot.send_message(cid, msg.text)
            elif msg.photo:
                await context.bot.send_photo(cid, msg.photo[-1].file_id, caption=msg.caption)
            elif msg.video:
                await context.bot.send_video(cid, msg.video.file_id, caption=msg.caption)
            elif msg.document:
                await context.bot.send_document(cid, msg.document.file_id, caption=msg.caption)
            elif msg.audio:
                await context.bot.send_audio(cid, msg.audio.file_id, caption=msg.caption)
            elif msg.voice:
                await context.bot.send_voice(cid, msg.voice.file_id)
            elif msg.sticker:
                await context.bot.send_sticker(cid, msg.sticker.file_id)
            else:
                continue
            success += 1
        except Exception as e:
            logger.warning(f"Broadcast fail {cid}: {e}")
            fail += 1
    await msg.reply_text(lang["broadcast_done"].format(success=success, fail=fail))

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# ============ 🏁 MAIN ============
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("credits", credits_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    media_filter = (
        filters.PHOTO |
        filters.VIDEO |
        filters.Document.ALL |
        filters.AUDIO |
        filters.VOICE |
        filters.Sticker.ALL
    )
    app.add_handler(MessageHandler(media_filter, handle_media))
    app.add_error_handler(error_handler)

    logger.info(f"🤖 Bot v{VERSION} started polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
