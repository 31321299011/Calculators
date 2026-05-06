import logging
import re
import math
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============ কনফিগ ============
BOT_TOKEN = "8691010655:AAHXVL-CqUd-PKkF2NDHr9jS2u0bJQAEDAc"
ADMIN_IDS = [8194390770, 7134813314]
DB_NAME = "bot_data.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============ ডাটাবেজ ============
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

# ============ সেফ ক্যালকুলেটর ============
ALLOWED_NAMES = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
ALLOWED_NAMES.update({
    "abs": abs, "round": round, "min": min, "max": max, "pow": pow,
    "int": int, "float": float, "pi": math.pi, "e": math.e
})

def safe_eval(expr: str):
    expr = expr.replace("^", "**")
    code = compile(expr, "<string>", "eval")
    for name in code.co_names:
        if name not in ALLOWED_NAMES:
            raise NameError(f"'{name}' not allowed")
    return eval(code, {"__builtins__": {}}, ALLOWED_NAMES)

# ============ /start ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        save_chat(chat.id, "private")
        if user.id in ADMIN_IDS:
            keyboard = [["📊 All Users", "📢 Broadcast"]]
            markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "👋 স্বাগতম অ্যাডমিন!\n"
                "📊 মোট ইউজার দেখতে ও ব্রডকাস্ট করতে বাটন ব্যবহার করুন।\n\n"
                "👨‍💻 ডেভেলপার: @bot_Developer_io ও @jhgmaing",
                reply_markup=markup
            )
        else:
            await update.message.reply_text(
                "👋 হ্যালো! আমি ক্যালকুলেটর বট।\n"
                "যেকোনো গণিত পাঠান, সাথে সাথে ফলাফল দেব।\n"
                "উদাহরণ: 2+2*5, sqrt(144), pi*2\n\n"
                "📌 আমাকে আপনার গ্রুপে অ্যাড করুন, গ্রুপেও অটো ক্যালকুলেট করব।\n"
                "গুরুত্বপূর্ণ: গ্রুপে অ্যাডের পর BotFather থেকে /setprivacy → Disable করুন।\n\n"
                "👨‍💻 ডেভেলপার: @bot_Developer_io ও @jhgmaing"
            )
    else:
        save_chat(chat.id, "group")
        await update.message.reply_text(
            "✅ বট সক্রিয়! এখন গ্রুপে যেকোনো অঙ্ক লিখুন, উত্তর পাবেন।\n"
            "⚠️ দয়া করে BotFather এ গিয়ে /setprivacy → Disable করে দিন, নাহলে আমি শুধু /start দেখতে পাব।"
        )

# ============ টেক্সট হ্যান্ডলার ============
BROADCAST_STATE = 1

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user
    chat = update.effective_chat
    text = msg.text.strip() if msg.text else ""

    save_chat(chat.id, "private" if chat.type == "private" else "group")

    # === অ্যাডমিন প্রাইভেট ব্রডকাস্ট ফ্লো ===
    if user.id in ADMIN_IDS and chat.type == "private":
        state = context.user_data.get("state")
        if state == BROADCAST_STATE:
            await broadcast_content(update, context)
            context.user_data["state"] = None
            return
        if text == "📊 All Users":
            await msg.reply_text(f"👥 মোট চ্যাট (ইউজার+গ্রুপ): {get_user_count()}")
            return
        if text == "📢 Broadcast":
            context.user_data["state"] = BROADCAST_STATE
            await msg.reply_text("📢 যা পাঠাতে চান (টেক্সট/ছবি/ভিডিও) সেন্ড করুন। বাতিল করতে /cancel")
            return
        if text == "/cancel":
            context.user_data["state"] = None
            await msg.reply_text("❌ ব্রডকাস্ট বাতিল।")
            return

    # === ক্যালকুলেটর লজিক ===
    if chat.type == "group" or (chat.type == "private" and user.id not in ADMIN_IDS):
        if not (user.id in ADMIN_IDS and context.user_data.get("state") == BROADCAST_STATE):
            result = await calc_reply(text)
            if result:
                await msg.reply_text(f"🧮 {result}")
            elif chat.type == "private":
                await msg.reply_text("🙏 আমি ক্যালকুলেটর বট। দয়া করে যেকোনো অঙ্ক লিখুন।\nযেমন: `2+3*4`, `sqrt(100)`, `pi*5`")

async def calc_reply(text: str):
    text = text.strip()
    if len(text) > 200:
        return None
    if not re.match(r'^[0-9+\-*/%^().\sa-zA-Z_πe]+$', text):
        return None
    try:
        res = safe_eval(text)
        if isinstance(res, float):
            return f"{res:.10f}".rstrip('0').rstrip('.')
        return str(res)
    except Exception:
        return None

# ============ মিডিয়া হ্যান্ডলার (শুধু অ্যাডমিন ব্রডকাস্টের জন্য) ============
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
    await msg.reply_text(f"✅ ব্রডকাস্ট শেষ!\nসফল: {success}\nব্যর্থ: {fail}")

# ============ এরর হ্যান্ডলার ============
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# ============ মেইন ============
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    # ✅ ফিক্সড মিডিয়া ফিল্টার (DOCUMENT → Document.ALL, STICKER → Sticker.ALL)
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

    logger.info("Bot started polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
