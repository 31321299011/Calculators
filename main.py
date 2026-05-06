# ============================================================
# 🔥 ULTRA PRO CALCULATOR BOT v4.0.0 — ১০০% ওয়ার্কিং
# 🌐 বাংলা · English · Русский · हिन्दी
# 👨‍💻 @bot_Developer_io & @jhgmaing
# ============================================================

import logging, re, math, sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==================== CONFIG ====================
BOT_TOKEN = "8691010655:AAHXVL-CqUd-PKkF2NDHr9jS2u0bJQAEDAc"
ADMIN_IDS = [8194390770, 7134813314]
DB_NAME = "bot_data.db"
VERSION = "4.0.0"
DEVELOPERS = "@bot_Developer_io & @jhgmaing"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ==================== MULTI-LANGUAGE ====================
T = {
    "bn": {
        "start_user": (
            "👋 হ্যালো! আমি স্মার্ট ক্যালকুলেটর বট।\n\n"
            "📌 আমাকে আপনার গ্রুপে অ্যাড করুন। গ্রুপে 2+2, sqrt(81) ইত্যাদি লিখলেই উত্তর দেব।\n\n"
            "🌐 সংস্করণ: {ver}\n"
            "👨‍💻 {dev}"
        ),
        "start_admin": "👑 অ্যাডমিন প্যানেল\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "add_btn": "➕ গ্রুপে অ্যাড করুন",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 যেকোনো অঙ্ক লিখুন (যেমন: 2+3*4, sqrt(100))",
        "all_users": "👥 মোট চ্যাট: {count}",
        "broadcast_prompt": "📢 যা পাঠাতে চান (টেক্সট/ছবি/ভিডিও) সেন্ড করুন। বাতিল করতে /cancel",
        "broadcast_done": "✅ ব্রডকাস্ট শেষ!\nসফল: {ok}\nব্যর্থ: {bad}",
        "broadcast_cancel": "❌ ব্রডকাস্ট বাতিল।",
        "privacy_note": "⚠️ গ্রুপে কাজ করতে BotFather থেকে /setprivacy → Disable করুন ও বট রিমুভ করে আবার অ্যাড করুন।",
    },
    "en": {
        "start_user": (
            "👋 Hi! I'm a smart calculator bot.\n\n"
            "📌 Add me to your group, and I'll auto-solve math like 2+2, sqrt(81).\n\n"
            "🌐 Version: {ver}\n"
            "👨‍💻 {dev}"
        ),
        "start_admin": "👑 Admin Panel\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "add_btn": "➕ Add to Group",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 Send a math expression (e.g. 2+3*4, sqrt(100))",
        "all_users": "👥 Total chats: {count}",
        "broadcast_prompt": "📢 Send content to broadcast. /cancel to abort.",
        "broadcast_done": "✅ Broadcast done!\nSuccess: {ok}\nFailed: {bad}",
        "broadcast_cancel": "❌ Broadcast cancelled.",
        "privacy_note": "⚠️ For group support, disable privacy: BotFather → /setprivacy → Disable, then re-add the bot.",
    },
    "ru": {
        "start_user": (
            "👋 Привет! Я бот-калькулятор.\n\n"
            "📌 Добавь меня в группу, и я решу 2+2, sqrt(81) автоматически.\n\n"
            "🌐 Версия: {ver}\n"
            "👨‍💻 {dev}"
        ),
        "start_admin": "👑 Админ-панель\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "add_btn": "➕ Добавить в группу",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 Отправьте выражение (напр. 2+3*4, sqrt(100))",
        "all_users": "👥 Всего чатов: {count}",
        "broadcast_prompt": "📢 Отправьте контент для рассылки. /cancel отмена.",
        "broadcast_done": "✅ Рассылка завершена!\nУспешно: {ok}\nНеудачно: {bad}",
        "broadcast_cancel": "❌ Рассылка отменена.",
        "privacy_note": "⚠️ Отключите приватность: BotFather → /setprivacy → Disable, затем перезапустите бота.",
    },
    "hi": {
        "start_user": (
            "👋 नमस्ते! मैं स्मार्ट कैलकुलेटर बॉट हूँ।\n\n"
            "📌 मुझे अपने ग्रुप में जोड़ें, मैं 2+2, sqrt(81) अपने आप हल करूँगा।\n\n"
            "🌐 संस्करण: {ver}\n"
            "👨‍💻 {dev}"
        ),
        "start_admin": "👑 एडमिन पैनल\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "add_btn": "➕ ग्रुप में जोड़ें",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 कोई गणित अभिव्यक्ति भेजें (जैसे 2+3*4, sqrt(100))",
        "all_users": "👥 कुल चैट: {count}",
        "broadcast_prompt": "📢 प्रसारण सामग्री भेजें। /cancel रद्द करें।",
        "broadcast_done": "✅ प्रसारण समाप्त!\nसफल: {ok}\nअसफल: {bad}",
        "broadcast_cancel": "❌ प्रसारण रद्द।",
        "privacy_note": "⚠️ ग्रुप में काम करने के लिए BotFather → /setprivacy → Disable करें, फिर बॉट को री-ऐड करें।",
    }
}

def lang(user):
    code = getattr(user, 'language_code', 'en') or 'en'
    return T.get(code[:2], T['en'])

# ==================== DATABASE ====================
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, type TEXT NOT NULL)")
        conn.commit()
init_db()

def save_chat(chat_id, typ):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR IGNORE INTO users (chat_id, type) VALUES (?, ?)", (chat_id, typ))
        conn.commit()

def get_all_chats():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT chat_id, type FROM users").fetchall()

def count_chats():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

# ==================== MATH ENGINE ====================
SAFE_MATH = {k:v for k,v in math.__dict__.items() if not k.startswith("__")}
SAFE_MATH.update({
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
        if name not in SAFE_MATH:
            raise NameError(f"'{name}' not allowed")
    return eval(code, {"__builtins__": {}}, SAFE_MATH)

def format_result(res):
    if isinstance(res, float):
        return f"{res:.10f}".rstrip('0').rstrip('.')
    return str(res)

def extract_math(text: str):
    text = text.strip()
    if not text:
        return None
    # পুরো টেক্সট এক্সপ্রেশন?
    if re.match(r'^[0-9+\-*/%^().\s\wπe]+$', text):
        try:
            return format_result(safe_eval(text))
        except:
            pass
    # সাবস্ট্রিং প্যাটার্ন
    patterns = [
        r'([-+]?\d*\.?\d+[+\-*/%^]+[-+]?\d*\.?\d+(?:[+\-*/%^][-+]?\d*\.?\d+)*)',
        r'((?:sqrt|sin|cos|tan|log|pi|e|abs|factorial|pow)\s*\([^)]+\))',
        r'([-+]?\d*\.?\d+\s*[+\-*/%^]\s*[-+]?\d*\.?\d+)',
    ]
    for pat in patterns:
        match = re.search(pat, text)
        if match:
            expr = match.group(1).strip()
            try:
                return format_result(safe_eval(expr))
            except:
                continue
    return None

# ==================== BROADCAST STATE ====================
BROADCAST_STATE = 1

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    t = lang(user)

    if chat.type == "private":
        save_chat(chat.id, "private")
        # ইনলাইন বাটন: গ্রুপে অ্যাড
        keyboard = [[InlineKeyboardButton(t["add_btn"], url=f"https://t.me/{context.bot.username}?startgroup=true")]]
        if user.id in ADMIN_IDS:
            # অ্যাডমিন: ReplyKeyboard + Inline
            reply_kb = [["📊 All Users", "📢 Broadcast"]]
            await update.message.reply_text(
                t["start_admin"].format(ver=VERSION, dev=DEVELOPERS),
                reply_markup=ReplyKeyboardMarkup(reply_kb, resize_keyboard=True)
            )
            await update.message.reply_text(
                t["privacy_note"],
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                t["start_user"].format(ver=VERSION, dev=DEVELOPERS),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        save_chat(chat.id, "group")
        # গ্রুপ: কিছু বলবে না

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    t = lang(user)
    await update.message.reply_text("🧠 " + t.get("not_math", "").replace("🙏 ", ""))

async def new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            save_chat(chat.id, "group")
            # একদম চুপ
            break

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user
    chat = update.effective_chat
    text = msg.text.strip() if msg.text else ""
    t = lang(user)

    save_chat(chat.id, "private" if chat.type == "private" else "group")

    # অ্যাডমিন ব্রডকাস্ট ফ্লো (প্রাইভেট)
    if user.id in ADMIN_IDS and chat.type == "private":
        state = context.user_data.get("state")
        if state == BROADCAST_STATE:
            await broadcast_send(update, context)
            context.user_data["state"] = None
            return
        if text == "📊 All Users":
            await msg.reply_text(t["all_users"].format(count=count_chats()))
            return
        if text == "📢 Broadcast":
            context.user_data["state"] = BROADCAST_STATE
            await msg.reply_text(t["broadcast_prompt"])
            return
        if text == "/cancel":
            context.user_data["state"] = None
            await msg.reply_text(t["broadcast_cancel"])
            return

    # ক্যালকুলেটর (গ্রুপ + নন-অ্যাডমিন প্রাইভেট)
    if chat.type == "group" or (chat.type == "private" and user.id not in ADMIN_IDS):
        if not (user.id in ADMIN_IDS and context.user_data.get("state") == BROADCAST_STATE):
            result = extract_math(text)
            if result:
                await msg.reply_text(t["calc_result"].format(res=result))
            elif chat.type == "private":
                await msg.reply_text(t["not_math"])

async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user
    chat = update.effective_chat
    save_chat(chat.id, "private" if chat.type == "private" else "group")

    if user.id in ADMIN_IDS and chat.type == "private" and context.user_data.get("state") == BROADCAST_STATE:
        await broadcast_send(update, context)
        context.user_data["state"] = None

async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user
    t = lang(user)
    all_chats = get_all_chats()
    ok, bad = 0, 0
    for cid, _ in all_chats:
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
            ok += 1
        except Exception as e:
            logger.warning(f"Broadcast fail {cid}: {e}")
            bad += 1
    await msg.reply_text(t["broadcast_done"].format(ok=ok, bad=bad))

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# ==================== MAIN ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    # মিডিয়া ফিল্টার (ব্রডকাস্টের জন্য)
    media_filter = (
        filters.PHOTO | filters.VIDEO | filters.Document.ALL |
        filters.AUDIO | filters.VOICE | filters.Sticker.ALL
    )
    app.add_handler(MessageHandler(media_filter, media_handler))
    app.add_error_handler(error_handler)

    logger.info(f"🤖 Bot v{VERSION} started polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
