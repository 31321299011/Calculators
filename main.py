# ==================================================
# 🔥 SUPER ULTRA CALCULATOR BOT v4.0.0
# 🌐 বাংলা | English | Русский | हिन्दी
# 👨‍💻 @bot_Developer_io & @jhgmaing
# ==================================================

import logging, re, math, sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ============ CONFIG ============
BOT_TOKEN = "8691010655:AAHXVL-CqUd-PKkF2NDHr9jS2u0bJQAEDAc"
ADMIN_IDS = [8194390770, 7134813314]
DB_NAME = "bot_data.db"
VERSION = "4.0.0"
DEVS = "@bot_Developer_io & @jhgmaing"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============ MULTI-LANG ============
T = {
    "bn": {
        "start_user": "👋 হ্যালো! আমি স্মার্ট ক্যালকুলেটর বট।\n\n📌 আমাকে আপনার গ্রুপে অ্যাড করুন। গ্রুপে 2+2, sqrt(81) ইত্যাদি লিখলেই উত্তর দেব।\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "start_admin": "👑 অ্যাডমিন প্যানেল\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 কোনো অঙ্ক লিখুন (যেমন: 2+3*4, sqrt(100))",
        "all_users": "👥 মোট চ্যাট: {count}",
        "broadcast_prompt": "📢 যা পাঠাতে চান সেন্ড করুন। /cancel এ বাতিল।",
        "broadcast_done": "✅ ব্রডকাস্ট শেষ!\nসফল: {ok}\nব্যর্থ: {bad}",
        "broadcast_cancel": "❌ ব্রডকাস্ট বাতিল।",
    },
    "en": {
        "start_user": "👋 Hi! I'm a smart calculator bot.\n\n📌 Add me to your group, and I'll auto-solve math like 2+2, sqrt(81).\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "start_admin": "👑 Admin Panel\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 Send a math expression (e.g., 2+3*4, sqrt(100))",
        "all_users": "👥 Total chats: {count}",
        "broadcast_prompt": "📢 Send content to broadcast. /cancel to abort.",
        "broadcast_done": "✅ Broadcast done!\nSuccess: {ok}\nFailed: {bad}",
        "broadcast_cancel": "❌ Broadcast cancelled.",
    },
    "ru": {
        "start_user": "👋 Привет! Я бот-калькулятор.\n\n📌 Добавь меня в группу, и я сам решу 2+2, sqrt(81).\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "start_admin": "👑 Админ-панель\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 Отправьте выражение (напр. 2+3*4, sqrt(100))",
        "all_users": "👥 Всего чатов: {count}",
        "broadcast_prompt": "📢 Отправьте контент для рассылки. /cancel отмена.",
        "broadcast_done": "✅ Рассылка завершена!\nУспешно: {ok}\nНеудачно: {bad}",
        "broadcast_cancel": "❌ Рассылка отменена.",
    },
    "hi": {
        "start_user": "👋 नमस्ते! मैं स्मार्ट कैलकुलेटर बॉट हूँ।\n\n📌 मुझे ग्रुप में जोड़ें, और 2+2, sqrt(81) जैसे सवाल अपने आप हल करूँगा।\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "start_admin": "👑 एडमिन पैनल\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 कोई गणित अभिव्यक्ति भेजें (जैसे 2+3*4, sqrt(100))",
        "all_users": "👥 कुल चैट: {count}",
        "broadcast_prompt": "📢 प्रसारण सामग्री भेजें। /cancel रद्द करें।",
        "broadcast_done": "✅ प्रसारण समाप्त!\nसफल: {ok}\nअसफल: {bad}",
        "broadcast_cancel": "❌ प्रसारण रद्द।",
    }
}

def _(user, key, **kw):
    lang = user.language_code or "en"
    base = T.get(lang[:2], T["en"])
    return base[key].format(**kw, ver=VERSION, dev=DEVS)

# ============ DATABASE ============
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, type TEXT NOT NULL)")
        conn.commit()
init_db()

def save(id, typ):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR IGNORE INTO users (chat_id, type) VALUES (?, ?)", (id, typ))
        conn.commit()

def get_all():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT chat_id, type FROM users").fetchall()

def count():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

# ============ MATH ENGINE ============
SAFE = {k:v for k,v in math.__dict__.items() if not k.startswith("__")}
SAFE.update({
    "abs":abs,"round":round,"min":min,"max":max,"pow":pow,"int":int,"float":float,
    "pi":math.pi,"e":math.e,"sin":math.sin,"cos":math.cos,"tan":math.tan,
    "asin":math.asin,"acos":math.acos,"atan":math.atan,"sinh":math.sinh,"cosh":math.cosh,
    "tanh":math.tanh,"log":math.log,"log10":math.log10,"sqrt":math.sqrt,
    "ceil":math.ceil,"floor":math.floor,"factorial":math.factorial,
    "degrees":math.degrees,"radians":math.radians
})

def calc(expr):
    expr = expr.replace("^", "**")
    code = compile(expr, "<string>", "eval")
    for name in code.co_names:
        if name not in SAFE:
            raise NameError(f"'{name}' not allowed")
    return eval(code, {"__builtins__": {}}, SAFE)

def fmt(res):
    if isinstance(res, float):
        return f"{res:.10f}".rstrip('0').rstrip('.')
    return str(res)

def extract(txt):
    txt = txt.strip()
    if not txt: return None
    # পুরো টেক্সট এক্সপ্রেশন
    if re.match(r'^[0-9+\-*/%^().\s\wπe]+$', txt):
        try: return fmt(calc(txt))
        except: pass
    # ভিতর থেকে খোঁজা
    for pat in [
        r'([-+]?\d*\.?\d+[+\-*/%^]+[-+]?\d*\.?\d+(?:[+\-*/%^][-+]?\d*\.?\d+)*)',
        r'((?:sqrt|sin|cos|tan|log|pi|e|abs|factorial|pow)\s*\([^)]+\))',
        r'([-+]?\d*\.?\d+\s*[+\-*/%^]\s*[-+]?\d*\.?\d+)'
    ]:
        m = re.search(pat, txt)
        if m:
            e = m.group(1).strip()
            try: return fmt(calc(e))
            except: continue
    return None

# ============ HANDLERS ============
BROADCAST = 1

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    c = update.effective_chat; u = update.effective_user
    if c.type == "private":
        save(c.id, "private")
        if u.id in ADMIN_IDS:
            kb = [["📊 All Users", "📢 Broadcast"]]
            await update.message.reply_text(_(u,"start_admin"), reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        else:
            await update.message.reply_text(_(u,"start_user"))
    else:
        save(c.id, "group")  # গ্রুপে একদম চুপ

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    await update.message.reply_text("🧠 2+3*4, sqrt(100), sin(30) ইত্যাদি লিখুন।")

async def new_member(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    c = update.effective_chat
    for m in update.message.new_chat_members:
        if m.id == ctx.bot.id:
            save(c.id, "group")
            # কোনো মেসেজ দেব না

async def text_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message; u = update.effective_user; c = update.effective_chat
    txt = msg.text.strip() if msg.text else ""
    save(c.id, "private" if c.type=="private" else "group")

    # অ্যাডমিন প্রাইভেট ব্রডকাস্ট ফ্লো
    if u.id in ADMIN_IDS and c.type=="private":
        st = ctx.user_data.get("state")
        if st == BROADCAST:
            await broadcast(update, ctx)
            ctx.user_data["state"] = None; return
        if txt == "📊 All Users":
            await msg.reply_text(_(u,"all_users",count=count())); return
        if txt == "📢 Broadcast":
            ctx.user_data["state"] = BROADCAST
            await msg.reply_text(_(u,"broadcast_prompt")); return
        if txt == "/cancel":
            ctx.user_data["state"] = None
            await msg.reply_text(_(u,"broadcast_cancel")); return

    # ক্যালকুলেটর (গ্রুপ + নন-অ্যাডমিন প্রাইভেট)
    if c.type=="group" or (c.type=="private" and u.id not in ADMIN_IDS):
        if not (u.id in ADMIN_IDS and ctx.user_data.get("state")==BROADCAST):
            res = extract(txt)
            if res:
                await msg.reply_text(_(u,"calc_result",res=res))
            elif c.type=="private":
                await msg.reply_text(_(u,"not_math"))

async def media(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message; u = update.effective_user; c = update.effective_chat
    save(c.id, "private" if c.type=="private" else "group")
    if u.id in ADMIN_IDS and c.type=="private" and ctx.user_data.get("state")==BROADCAST:
        await broadcast(update,ctx)
        ctx.user_data["state"] = None

async def broadcast(update, ctx):
    msg = update.message; u = update.effective_user
    all_chats = get_all()
    ok = bad = 0
    for cid,_ in all_chats:
        try:
            if msg.text: await ctx.bot.send_message(cid, msg.text)
            elif msg.photo: await ctx.bot.send_photo(cid, msg.photo[-1].file_id, caption=msg.caption)
            elif msg.video: await ctx.bot.send_video(cid, msg.video.file_id, caption=msg.caption)
            elif msg.document: await ctx.bot.send_document(cid, msg.document.file_id, caption=msg.caption)
            elif msg.audio: await ctx.bot.send_audio(cid, msg.audio.file_id, caption=msg.caption)
            elif msg.voice: await ctx.bot.send_voice(cid, msg.voice.file_id)
            elif msg.sticker: await ctx.bot.send_sticker(cid, msg.sticker.file_id)
            else: continue
            ok += 1
        except Exception as e:
            logger.warning(f"Broadcast fail {cid}: {e}")
            bad += 1
    await msg.reply_text(_(u,"broadcast_done",ok=ok,bad=bad))

async def err(update, ctx):
    logger.error(f"Update {update} caused error {ctx.error}")

# ============ MAIN ============
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_msg))
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO | filters.VOICE | filters.Sticker.ALL,
        media
    ))
    app.add_error_handler(err)
    logger.info(f"🤖 Bot v{VERSION} running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
