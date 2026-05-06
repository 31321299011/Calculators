# ============================================================
# 🔥 মহাকাশ-সম্পন্ন ক্যালকুলেটর বট v5.0.0 (ফাইনাল)
# 🌐 বাংলা · English · Русский · हिन्दी
# 👨‍💻 @bot_Developer_io & @jhgmaing
# ============================================================
# ▸ প্রাইভেটে সরাসরি অঙ্ক লিখলেই উত্তর পাবেন।
# ▸ গ্রুপে /calc বা @bot_name অঙ্ক লিখলে কাজ করবে (প্রাইভেসি নির্বিশেষে)।
# ▸ /inlinecal – বাটন-ভিত্তিক ক্যালকুলেটর (গ্রুপে ও প্রাইভেটে)।
# ▸ গ্রুপে অটো-ডিটেক্ট চাইলে BotFather থেকে /setprivacy → Disable করে বট রিমুভ+অ্যাড করুন।
# ============================================================

import logging, re, math, sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler,
    filters, ContextTypes
)

# ========== টোকেন ও কনফিগ ==========
BOT_TOKEN = "8691010655:AAHXVL-CqUd-PKkF2NDHr9jS2u0bJQAEDAc"
ADMIN_IDS = [8194390770, 7134813314]
DB_NAME = "bot_data.db"
VERSION = "5.0.0"
DEVS = "@bot_Developer_io & @jhgmaing"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# ========== মাল্টি-ল্যাঙ্গুয়েজ (বাংলা, English, Русский, हिन्दी) ==========
LANG = {
    "bn": {
        "start": "👋 হ্যালো! আমি স্মার্ট ক্যালকুলেটর বট।\n\n📌 প্রাইভেটে অঙ্ক লিখলেই উত্তর পাবেন।\n📌 গ্রুপে /calc 2+2 বা @bot 2+2 ব্যবহার করুন।\n📌 /inlinecal – বাটন ক্যালকুলেটর।\n\n👨‍💻 {dev}\n🌐 v{ver}",
        "start_admin": "👑 অ্যাডমিন প্যানেল\n\n👨‍💻 {dev}\n🌐 v{ver}",
        "add_btn": "➕ গ্রুপে অ্যাড করুন",
        "inline_title": "🔢 ইন্টারেক্টিভ ক্যালকুলেটর",
        "expr_empty": "এখনো কিছু লেখা হয়নি",
        "expr_label": "অভিব্যক্তি: {expr}",
        "result_label": "ফলাফল:     {res}",
        "error": "ত্রুটি",
        "not_math": "🙏 যেকোনো অঙ্ক লিখুন (যেমন: 2+3*4, sqrt(100))",
        "calc_result": "🧮 {res}",
        "all_users": "👥 মোট চ্যাট: {cnt}",
        "broadcast": "📢 যা পাঠাতে চান সেন্ড করুন। /cancel বাতিল।",
        "broadcast_done": "✅ সফল: {ok}\n❌ ব্যর্থ: {bad}",
        "broadcast_cancel": "❌ বাতিল করা হয়েছে।",
        "privacy_warning": "⚠️ গ্রুপে অটো-ডিটেক্ট চাইলে BotFather → /setprivacy → Disable + বট Remove→Add করুন।",
    },
    "en": {
        "start": "👋 Hi! I'm a smart calculator bot.\n\n📌 In private, just type a math expression.\n📌 In group, use /calc 2+2 or @bot 2+2.\n📌 /inlinecal – button calculator.\n\n👨‍💻 {dev}\n🌐 v{ver}",
        "start_admin": "👑 Admin Panel\n\n👨‍💻 {dev}\n🌐 v{ver}",
        "add_btn": "➕ Add to Group",
        "inline_title": "🔢 Interactive Calculator",
        "expr_empty": "Nothing entered yet",
        "expr_label": "Expression: {expr}",
        "result_label": "Result:    {res}",
        "error": "Error",
        "not_math": "🙏 Send a math expression (e.g. 2+3*4, sqrt(100))",
        "calc_result": "🧮 {res}",
        "all_users": "👥 Total chats: {cnt}",
        "broadcast": "📢 Send content to broadcast. /cancel to abort.",
        "broadcast_done": "✅ Success: {ok}\n❌ Failed: {bad}",
        "broadcast_cancel": "❌ Cancelled.",
        "privacy_warning": "⚠️ For auto-detect in groups: BotFather → /setprivacy → Disable, then Remove & Re-add the bot.",
    },
    "ru": {
        "start": "👋 Привет! Я умный бот-калькулятор.\n\n📌 В личке просто напиши выражение.\n📌 В группе: /calc 2+2 или @bot 2+2.\n📌 /inlinecal – кнопочный калькулятор.\n\n👨‍💻 {dev}\n🌐 v{ver}",
        "start_admin": "👑 Админ-панель\n\n👨‍💻 {dev}\n🌐 v{ver}",
        "add_btn": "➕ Добавить в группу",
        "inline_title": "🔢 Интерактивный калькулятор",
        "expr_empty": "Пока ничего не введено",
        "expr_label": "Выражение: {expr}",
        "result_label": "Результат: {res}",
        "error": "Ошибка",
        "not_math": "🙏 Отправьте выражение (напр. 2+3*4, sqrt(100))",
        "calc_result": "🧮 {res}",
        "all_users": "👥 Всего чатов: {cnt}",
        "broadcast": "📢 Отправьте контент. /cancel отмена.",
        "broadcast_done": "✅ Успешно: {ok}\n❌ Ошибок: {bad}",
        "broadcast_cancel": "❌ Отменено.",
        "privacy_warning": "⚠️ Для авторасчета в группах: BotFather → /setprivacy → Disable, затем удали и снова добавь бота.",
    },
    "hi": {
        "start": "👋 नमस्ते! मैं स्मार्ट कैलकुलेटर बॉट हूँ।\n\n📌 प्राइवेट में सीधे गणित लिखें।\n📌 ग्रुप में /calc 2+2 या @bot 2+2 का उपयोग करें।\n📌 /inlinecal – बटन कैलकुलेटर।\n\n👨‍💻 {dev}\n🌐 v{ver}",
        "start_admin": "👑 एडमिन पैनल\n\n👨‍💻 {dev}\n🌐 v{ver}",
        "add_btn": "➕ ग्रुप में जोड़ें",
        "inline_title": "🔢 इंटरैक्टिव कैलकुलेटर",
        "expr_empty": "अभी तक कुछ नहीं लिखा",
        "expr_label": "अभिव्यक्ति: {expr}",
        "result_label": "परिणाम:    {res}",
        "error": "त्रुटि",
        "not_math": "🙏 कोई गणित भेजें (जैसे 2+3*4, sqrt(100))",
        "calc_result": "🧮 {res}",
        "all_users": "👥 कुल चैट: {cnt}",
        "broadcast": "📢 प्रसारण सामग्री भेजें। /cancel रद्द करें।",
        "broadcast_done": "✅ सफल: {ok}\n❌ असफल: {bad}",
        "broadcast_cancel": "❌ रद्द।",
        "privacy_warning": "⚠️ ग्रुप में ऑटो-डिटेक्ट के लिए BotFather → /setprivacy → Disable, फिर बॉट को हटाकर दोबारा जोड़ें।",
    }
}

def _(user, key, **kw):
    code = getattr(user, 'language_code', 'en') or 'en'
    base = LANG.get(code[:2], LANG['en'])
    return base[key].format(**kw, ver=VERSION, dev=DEVS)

# ========== ডাটাবেজ ==========
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, type TEXT NOT NULL)")
        conn.commit()
init_db()

def save_chat(cid, typ):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR IGNORE INTO users VALUES (?,?)", (cid, typ))
        conn.commit()

def get_all_chats():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT chat_id, type FROM users").fetchall()

def count_chats():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

# ========== ম্যাথ ইঞ্জিন ==========
SAFE_MATH = {k:v for k,v in math.__dict__.items() if not k.startswith("__")}
SAFE_MATH.update({
    "abs":abs,"round":round,"min":min,"max":max,"pow":pow,"int":int,"float":float,
    "pi":math.pi,"e":math.e,"sin":math.sin,"cos":math.cos,"tan":math.tan,
    "asin":math.asin,"acos":math.acos,"atan":math.atan,"log":math.log,
    "log10":math.log10,"sqrt":math.sqrt,"ceil":math.ceil,"floor":math.floor,
    "factorial":math.factorial,"degrees":math.degrees,"radians":math.radians
})

def safe_eval(expr: str):
    expr = expr.replace("^", "**")
    code = compile(expr, "<string>", "eval")
    for name in code.co_names:
        if name not in SAFE_MATH:
            raise NameError(f"'{name}' not allowed")
    return eval(code, {"__builtins__": {}}, SAFE_MATH)

def format_res(n):
    if isinstance(n, float):
        return f"{n:.10f}".rstrip('0').rstrip('.')
    return str(n)

# ========== ইন্টারেক্টিভ ক্যালকুলেটর বাটন ==========
def build_calc_keyboard(expr: str):
    btns = [
        ["7","8","9","/","("],
        ["4","5","6","*",")"],
        ["1","2","3","-","^"],
        ["0",".","C","+","√"],
        ["sin","cos","tan","log","pi"],
        ["⌫","="," "," "," "]
    ]
    kb = []
    for row in btns:
        kb_row = []
        for b in row:
            if b == " ":
                kb_row.append(InlineKeyboardButton(" ", callback_data="CLR_IGNORE"))
            else:
                data = b
                if b == "⌫": data = "BACKSPACE"
                elif b == "C": data = "CLEAR"
                elif b == "=": data = "EVAL"
                elif b == "√": data = "SQRT("
                kb_row.append(InlineKeyboardButton(b, callback_data=f"CALC_{data}"))
        kb.append(kb_row)
    return InlineKeyboardMarkup(kb)

def process_button(expr: str, cmd: str):
    if cmd == "CLEAR": return ""
    if cmd == "EVAL":
        try: return format_res(safe_eval(expr))
        except: return "ERROR"
    if cmd == "BACKSPACE": return expr[:-1]
    if cmd == "SQRT(": return expr + "sqrt("
    if cmd == "IGNORE": return expr
    return expr + cmd

def inlinecalc_message(expr: str, lang_dict):
    title = lang_dict["inline_title"]
    expr_line = lang_dict["expr_label"].format(expr=expr if expr else lang_dict["expr_empty"])
    try:
        if expr and expr != "ERROR":
            res = format_res(safe_eval(expr))
        else:
            res = expr if expr == "ERROR" else ""
    except:
        res = lang_dict["error"]
    result_line = lang_dict["result_label"].format(res=res)
    return f"{title}\n\n{expr_line}\n{result_line}"

# ========== হ্যান্ডলার ==========
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    # save
    save_chat(chat.id, "private" if chat.type == "private" else "group")

    t = _(user)
    add_btn = InlineKeyboardButton(t["add_btn"], url=f"https://t.me/{ctx.bot.username}?startgroup=true")
    if chat.type == "private":
        if user.id in ADMIN_IDS:
            # ReplyKeyboard for admin
            kb = [["📊 All Users", "📢 Broadcast"]]
            await update.message.reply_text(
                t["start_admin"],
                reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
            )
            # Inline button
            await update.message.reply_text(
                t["privacy_warning"],
                reply_markup=InlineKeyboardMarkup([[add_btn]])
            )
        else:
            await update.message.reply_text(
                t["start"],
                reply_markup=InlineKeyboardMarkup([[add_btn]])
            )
    else:
        # Group: don't send a message, just save
        pass

async def inlinecal_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Show the interactive button calculator"""
    user = update.effective_user
    t = _(user)
    msg = inlinecalc_message("", t)
    await update.message.reply_text(msg, reply_markup=build_calc_keyboard(""))

async def calc_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    t = _(user)
    data = query.data.replace("CALC_", "")

    # Extract current expression from message text
    current_text = query.message.text
    lines = current_text.split("\n")
    expr = ""
    # Look for expression line (depends on lang, we check for "Expression:" etc.)
    for line in lines:
        for prefix in ["Expression:", "অভিব্যক্তি:", "Выражение:", "अभिव्यक्ति:"]:
            if line.startswith(prefix):
                expr_str = line[len(prefix):].strip()
                if expr_str != t["expr_empty"]:
                    expr = expr_str
                break
        if expr or "Result" in line:
            break

    new_expr = process_button(expr, data)
    if new_expr == "ERROR":
        new_expr = expr  # keep old

    new_msg = inlinecalc_message(new_expr, t)
    try:
        await query.edit_message_text(new_msg, reply_markup=build_calc_keyboard(new_expr))
    except:
        await query.answer("Already up to date")
    await query.answer()

# প্রাইভেটে অটো-ক্যালকুলেট
async def private_auto_math(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if chat.type != "private":
        return
    text = update.message.text.strip()
    save_chat(chat.id, "private")

    # Admin button handling
    if user.id in ADMIN_IDS:
        if text == "📊 All Users":
            t = _(user)
            await update.message.reply_text(t["all_users"].format(cnt=count_chats()))
            return
        if text == "📢 Broadcast":
            ctx.user_data["broadcast"] = True
            t = _(user)
            await update.message.reply_text(t["broadcast"])
            return
        if ctx.user_data.get("broadcast"):
            await broadcast_send(update, ctx)
            ctx.user_data["broadcast"] = False
            return

    # Math detection
    t = _(user)
    if re.match(r'^[0-9+\-*/%^().\s\wπe]+$', text):
        try:
            res = format_res(safe_eval(text))
            await update.message.reply_text(t["calc_result"].format(res=res))
            return
        except:
            pass
    # else not math, show hint only if not admin/broadcast flow
    if not (user.id in ADMIN_IDS and ctx.user_data.get("broadcast")):
        await update.message.reply_text(t["not_math"])

# /calc command
async def calc_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not ctx.args:
        t = _(user)
        await update.message.reply_text(t["not_math"]); return
    expr = " ".join(ctx.args)
    t = _(user)
    try:
        res = format_res(safe_eval(expr))
        await update.message.reply_text(t["calc_result"].format(res=res))
    except:
        await update.message.reply_text(t["error"])

# /users (admin)
async def users_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS: return
    t = _(user)
    await update.message.reply_text(t["all_users"].format(cnt=count_chats()))

# /broadcast (admin)
async def broadcast_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS: return
    ctx.user_data["broadcast"] = True
    t = _(user)
    await update.message.reply_text(t["broadcast"])

async def cancel_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["broadcast"] = False
    t = _(update.effective_user)
    await update.message.reply_text(t["broadcast_cancel"])

async def broadcast_send(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # actual sending
    msg = update.message
    user = update.effective_user
    t = _(user)
    all_chats = get_all_chats()
    ok, bad = 0, 0
    for cid, _ in all_chats:
        try:
            if msg.text:
                await ctx.bot.send_message(cid, msg.text)
            elif msg.photo:
                await ctx.bot.send_photo(cid, msg.photo[-1].file_id, caption=msg.caption)
            elif msg.video:
                await ctx.bot.send_video(cid, msg.video.file_id, caption=msg.caption)
            elif msg.document:
                await ctx.bot.send_document(cid, msg.document.file_id, caption=msg.caption)
            elif msg.audio:
                await ctx.bot.send_audio(cid, msg.audio.file_id, caption=msg.caption)
            elif msg.voice:
                await ctx.bot.send_voice(cid, msg.voice.file_id)
            elif msg.sticker:
                await ctx.bot.send_sticker(cid, msg.sticker.file_id)
            else:
                continue
            ok += 1
        except Exception as e:
            logger.warning(f"Broadcast fail {cid}: {e}")
            bad += 1
    await update.message.reply_text(t["broadcast_done"].format(ok=ok, bad=bad))

# সব মিডিয়া (ব্রডকাস্ট ফ্লোতে থাকলে কাজ করবে)
async def media_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in ADMIN_IDS and ctx.user_data.get("broadcast"):
        await broadcast_send(update, ctx)
        ctx.user_data["broadcast"] = False

# ইনলাইন কুয়েরি (গ্রুপে @bot_name 2+2)
async def inline_query(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    if not query:
        return
    try:
        res = format_res(safe_eval(query))
        result = InlineQueryResultArticle(
            id="calc",
            title=f"🧮 {res}",
            description=query,
            input_message_content=InputTextMessageContent(f"🧮 {query} = {res}")
        )
        await update.inline_query.answer([result], cache_time=0)
    except:
        pass

# গ্রুপের টেক্সট (শুধু কমান্ড বাদে কিছুতে সাড়া দেয় না, যাতে স্প্যাম না হয়)
# তবে /calc কমান্ড আগেই ধরা পড়বে, আর /inlinecal ও

async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {ctx.error}")

# ========== মেইন ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # কমান্ডস
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("calc", calc_cmd))
    app.add_handler(CommandHandler("inlinecal", inlinecal_cmd))
    app.add_handler(CommandHandler("users", users_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))

    # প্রাইভেট টেক্সট (অটো-ম্যাথ)
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, private_auto_math))
    # গ্রুপে সাধারণ টেক্সট ইগনোর (কারণ প্রাইভেসি এনাবল থাকলে বট দেখবে না; ডিসেইবল করলে অটো ধরবে, কিন্তু স্প্যাম এড়াতে আমরা ইগনোর করি)
    # আমরা আলাদা হ্যান্ডলার দিব না

    # মিডিয়া (ব্রডকাস্ট)
    media_filter = filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO | filters.VOICE | filters.Sticker.ALL
    app.add_handler(MessageHandler(media_filter, media_handler))

    # ইনলাইন কুয়েরি
    app.add_handler(InlineQueryHandler(inline_query))

    # ক্যালকুলেটর বাটন কলব্যাক
    app.add_handler(CallbackQueryHandler(calc_callback, pattern="^CALC_"))

    # এরর হ্যান্ডলার
    app.add_error_handler(error_handler)

    logger.info("🤖 BOT v5.0.0 RUNNING — গ্রুপে /calc, /inlinecal অথবা @bot_name লিখুন")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
