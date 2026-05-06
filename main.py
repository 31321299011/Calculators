import logging, re, math, sqlite3
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, InlineQueryHandler, CallbackContext, filters, ContextTypes
)

TOKEN = "8691010655:AAHXVL-CqUd-PKkF2NDHr9jS2u0bJQAEDAc"
ADMIN_IDS = [8194390770, 7134813314]
DB = "data.db"
VERSION = "FINAL"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# ========== DATABASE ==========
with sqlite3.connect(DB) as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, type TEXT)")
    conn.commit()

def save(chat_id, typ):
    with sqlite3.connect(DB) as conn:
        conn.execute("INSERT OR IGNORE INTO users VALUES (?,?)", (chat_id, typ))
        conn.commit()

def get_all():
    with sqlite3.connect(DB) as conn:
        return conn.execute("SELECT chat_id, type FROM users").fetchall()

def count_all():
    with sqlite3.connect(DB) as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

# ========== MATH ENGINE ==========
SAFE = {k:v for k,v in math.__dict__.items() if not k.startswith("__")}
SAFE.update({
    "abs":abs,"round":round,"min":min,"max":max,"pow":pow,"int":int,"float":float,
    "pi":math.pi,"e":math.e,"sin":math.sin,"cos":math.cos,"tan":math.tan,
    "asin":math.asin,"acos":math.acos,"atan":math.atan,"log":math.log,
    "log10":math.log10,"sqrt":math.sqrt,"ceil":math.ceil,"floor":math.floor,
    "factorial":math.factorial,"degrees":math.degrees,"radians":math.radians,
})

def calc(expr):
    expr = expr.replace("^", "**")
    code = compile(expr, "<string>", "eval")
    for name in code.co_names:
        if name not in SAFE:
            raise NameError(f"'{name}' not allowed")
    return eval(code, {"__builtins__": {}}, SAFE)

def fmt(n):
    if isinstance(n, float):
        return f"{n:.10f}".rstrip('0').rstrip('.')
    return str(n)

# ========== HANDLERS ==========
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat; user = update.effective_user
    if chat.type == "private":
        save(chat.id, "private")
        kb = [["📊 All Users", "📢 Broadcast"]] if user.id in ADMIN_IDS else []
        await update.message.reply_text(
            "👋 Calculator Bot\n\n"
            "• গ্রুপে /calc 2+2 অথবা @username 2+2 লিখুন\n"
            "• প্রাইভেটে সরাসরি অঙ্ক লিখলেই উত্তর পাবেন",
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True) if kb else None
        )
    else:
        save(chat.id, "group")
        # গ্রুপে কিছু বলবে না

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 ব্যবহার:\n"
        "/calc 2+2\n"
        "প্রাইভেটে সরাসরি অঙ্ক লিখুন।\n"
        "ইনলাইন: @bot 2+2"
    )

async def calc_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("ফরম্যাট: /calc 2+2"); return
    expr = " ".join(ctx.args)
    try:
        res = fmt(calc(expr))
        await update.message.reply_text(f"🧮 {res}")
    except:
        await update.message.reply_text("❌ ভুল এক্সপ্রেশন")

# প্রাইভেটে অটো-ডিটেক্ট
async def auto_math(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    # চেক করি এটা অঙ্ক কিনা
    if not re.match(r'^[0-9+\-*/%^().\s\wπe]+$', text):
        return
    try:
        res = fmt(calc(text))
        await update.message.reply_text(f"🧮 {res}")
    except:
        pass

# ইনলাইন কুয়েরি
async def inline_calc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    if not query:
        return
    try:
        res = fmt(calc(query))
        results = [InlineQueryResultArticle(
            id="calc",
            title=f"🧮 {res}",
            description=query,
            input_message_content=InputTextMessageContent(f"🧮 {query} = {res}")
        )]
        await update.inline_query.answer(results, cache_time=0)
    except:
        pass

# অ্যাডমিন
async def all_users(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMIN_IDS:
        await update.message.reply_text(f"👥 মোট চ্যাট: {count_all()}")

async def broadcast_prompt(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMIN_IDS:
        ctx.user_data['broadcast'] = True
        await update.message.reply_text("📢 যা পাঠাতে চান সেন্ড করুন। /cancel")

async def broadcast_send(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.user_data.get('broadcast'):
        return
    msg = update.message
    all_chats = get_all()
    ok, bad = 0,0
    for cid,_ in all_chats:
        try:
            if msg.text: await ctx.bot.send_message(cid, msg.text)
            elif msg.photo: await ctx.bot.send_photo(cid, msg.photo[-1].file_id, caption=msg.caption)
            elif msg.video: await ctx.bot.send_video(cid, msg.video.file_id, caption=msg.caption)
            else: continue
            ok += 1
        except: bad += 1
    await update.message.reply_text(f"✅ সফল: {ok}\n❌ ব্যর্থ: {bad}")
    ctx.user_data['broadcast'] = False

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['broadcast'] = False
    await update.message.reply_text("❌ বাতিল")

async def media_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ctx.user_data.get('broadcast') and update.effective_user.id in ADMIN_IDS:
        await broadcast_send(update, ctx)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("calc", calc_cmd))
    app.add_handler(CommandHandler("users", all_users))
    app.add_handler(CommandHandler("broadcast", broadcast_prompt))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, auto_math))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE & filters.Regex("^(📊 All Users|📢 Broadcast)$"),
        lambda u,c: all_users(u,c) if u.message.text == "📊 All Users" else broadcast_prompt(u,c)
    ))
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO | filters.VOICE,
        media_broadcast
    ))
    app.add_handler(InlineQueryHandler(inline_calc))
    logger.info("✅ BOT RUNNING – গ্রুপে /calc বা ইনলাইন ব্যবহার করুন")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
