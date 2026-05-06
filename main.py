# ============================================================
# 🚀 SUPER ULTIMATE CALCULATOR BOT v5.0.0
# 🌐 বাংলা · English · Русский · हिन्दी
# 👨‍💻 @bot_Developer_io & @jhgmaing
# ============================================================

import logging, re, math, sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
)

# ==================== CONFIG ====================
BOT_TOKEN = "8691010655:AAHXVL-CqUd-PKkF2NDHr9jS2u0bJQAEDAc"  # ✅ এই টোকেনটাই ঠিক
ADMIN_IDS = [8194390770, 7134813314]
DB_NAME = "bot_data.db"
VERSION = "5.0.0"
DEVS = "@bot_Developer_io & @jhgmaing"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ==================== LANGUAGE ====================
T = {
    "bn": {
        "start_user": "👋 হ্যালো! আমি স্মার্ট ক্যালকুলেটর বট।\n\n📌 আমাকে গ্রুপে অ্যাড করুন।\n2+2, sqrt(81) লিখলে অটো উত্তর দেব।\n/inlinecal – ইন্টারেক্টিভ ক্যালকুলেটর।\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "start_admin": "👑 অ্যাডমিন প্যানেল\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "add_btn": "➕ গ্রুপে অ্যাড করুন",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 কোনো অঙ্ক লিখুন (2+3*4, sqrt(100))",
        "all_users": "👥 মোট চ্যাট: {cnt}",
        "broadcast_prompt": "📢 যা পাঠাবেন সেন্ড করুন। /cancel বাতিল।",
        "broadcast_done": "✅ সম্পন্ন!\nসফল: {ok}\nব্যর্থ: {bad}",
        "broadcast_cancel": "❌ ব্রডকাস্ট বাতিল।",
        "inlinecalc_title": "🔢 ইন্টারেক্টিভ ক্যালকুলেটর",
        "inlinecalc_expr": "অভিব্যক্তি: {expr}",
        "inlinecalc_empty": "এখনো কিছু দেওয়া হয়নি",
        "inlinecalc_result": "ফলাফল: {res}",
        "inlinecalc_error": "ত্রুটি",
        "privacy_note": "⚠️ গ্রুপে কাজ করতে BotFather-এ /setprivacy → Disable করে বট Remove + Add করুন।",
    },
    "en": {
        "start_user": "👋 Hi! I'm a smart calculator bot.\n\n📌 Add me to a group.\n2+2, sqrt(81) will auto-answer.\n/inlinecal – interactive inline calculator.\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "start_admin": "👑 Admin Panel\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "add_btn": "➕ Add to Group",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 Send a math expression (e.g. 2+3*4, sqrt(100))",
        "all_users": "👥 Total chats: {cnt}",
        "broadcast_prompt": "📢 Send content to broadcast. /cancel to abort.",
        "broadcast_done": "✅ Done!\nSuccess: {ok}\nFailed: {bad}",
        "broadcast_cancel": "❌ Broadcast cancelled.",
        "inlinecalc_title": "🔢 Interactive Calculator",
        "inlinecalc_expr": "Expression: {expr}",
        "inlinecalc_empty": "Nothing entered yet",
        "inlinecalc_result": "Result: {res}",
        "inlinecalc_error": "Error",
        "privacy_note": "⚠️ Disable privacy mode in BotFather, then remove & re-add the bot.",
    },
    "ru": {
        "start_user": "👋 Привет! Я умный бот-калькулятор.\n\n📌 Добавь в группу.\n2+2, sqrt(81) решу автоматически.\n/inlinecal – интерактивный калькулятор.\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "start_admin": "👑 Админ-панель\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "add_btn": "➕ Добавить в группу",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 Отправьте выражение (2+3*4, sqrt(100))",
        "all_users": "👥 Всего чатов: {cnt}",
        "broadcast_prompt": "📢 Отправьте контент. /cancel отмена.",
        "broadcast_done": "✅ Готово!\nУспешно: {ok}\nНеудачно: {bad}",
        "broadcast_cancel": "❌ Рассылка отменена.",
        "inlinecalc_title": "🔢 Интерактивный калькулятор",
        "inlinecalc_expr": "Выражение: {expr}",
        "inlinecalc_empty": "Пока ничего не введено",
        "inlinecalc_result": "Результат: {res}",
        "inlinecalc_error": "Ошибка",
        "privacy_note": "⚠️ Отключите приватность в BotFather, затем удалите и снова добавьте бота.",
    },
    "hi": {
        "start_user": "👋 नमस्ते! मैं स्मार्ट कैलकुलेटर बॉट हूँ।\n\n📌 मुझे ग्रुप में जोड़ें।\n2+2, sqrt(81) अपने आप हल करूँगा।\n/inlinecal – इंटरैक्टिव कैलकुलेटर।\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "start_admin": "👑 एडमिन पैनल\n\n🌐 v{ver}\n👨‍💻 {dev}",
        "add_btn": "➕ ग्रुप में जोड़ें",
        "calc_result": "🧮 {res}",
        "not_math": "🙏 कोई गणित भेजें (2+3*4, sqrt(100))",
        "all_users": "👥 कुल चैट: {cnt}",
        "broadcast_prompt": "📢 प्रसारण सामग्री भेजें। /cancel रद्द।",
        "broadcast_done": "✅ पूर्ण!\nसफल: {ok}\nअसफल: {bad}",
        "broadcast_cancel": "❌ प्रसारण रद्द।",
        "inlinecalc_title": "🔢 इंटरैक्टिव कैलकुलेटर",
        "inlinecalc_expr": "अभिव्यक्ति: {expr}",
        "inlinecalc_empty": "अभी तक कुछ नहीं डाला",
        "inlinecalc_result": "परिणाम: {res}",
        "inlinecalc_error": "त्रुटि",
        "privacy_note": "⚠️ BotFather में प्राइवेसी मोड बंद करें, फिर बॉट हटाकर दोबारा जोड़ें।",
    }
}

def _(user, key, **kw):
    code = getattr(user, 'language_code', 'en') or 'en'
    base = T.get(code[:2], T['en'])
    return base[key].format(**kw, ver=VERSION, dev=DEVS)

# ==================== DB ====================
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, type TEXT NOT NULL)")
        conn.commit()
init_db()

def save(chat_id, typ):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR IGNORE INTO users (chat_id, type) VALUES (?, ?)", (chat_id, typ))
        conn.commit()

def get_all():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT chat_id, type FROM users").fetchall()

def count_all():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

# ==================== MATH ENGINE ====================
SAFE = {k:v for k,v in math.__dict__.items() if not k.startswith("__")}
SAFE.update({
    "abs":abs,"round":round,"min":min,"max":max,"pow":pow,"int":int,"float":float,
    "pi":math.pi,"e":math.e,"sin":math.sin,"cos":math.cos,"tan":math.tan,
    "asin":math.asin,"acos":math.acos,"atan":math.atan,"sinh":math.sinh,"cosh":math.cosh,
    "tanh":math.tanh,"log":math.log,"log10":math.log10,"sqrt":math.sqrt,
    "ceil":math.ceil,"floor":math.floor,"factorial":math.factorial,
    "degrees":math.degrees,"radians":math.radians
})

def safe_eval(expr):
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

def extract_math(text):
    text = text.strip()
    if not text:
        return None
    if re.match(r'^[0-9+\-*/%^().\s\wπe]+$', text):
        try: return fmt(safe_eval(text))
        except: pass
    for pat in [
        r'([-+]?\d*\.?\d+[+\-*/%^]+[-+]?\d*\.?\d+(?:[+\-*/%^][-+]?\d*\.?\d+)*)',
        r'((?:sqrt|sin|cos|tan|log|pi|e|abs|factorial|pow)\s*\([^)]+\))',
        r'([-+]?\d*\.?\d+\s*[+\-*/%^]\s*[-+]?\d*\.?\d+)',
    ]:
        m = re.search(pat, text)
        if m:
            e = m.group(1).strip()
            try: return fmt(safe_eval(e))
            except: continue
    return None

# ==================== BROADCAST ====================
BROADCAST = 1

# ==================== INLINE CALCULATOR ====================
def build_calc_markup(expr: str):
    """Build inline keyboard for calculator."""
    buttons = [
        ["7", "8", "9", "/", "("],
        ["4", "5", "6", "*", ")"],
        ["1", "2", "3", "-", "^"],
        ["0", ".", "C", "+", "√"],
        ["sin", "cos", "tan", "log", "pi"],
        ["⌫", "=", " ", " ", " "]
    ]
    keyboard = []
    for row in buttons:
        kb_row = []
        for btn in row:
            if btn.strip():
                data = btn
                if btn == "⌫":
                    data = "BACKSPACE"
                elif btn == "C":
                    data = "CLEAR"
                elif btn == "=":
                    data = "EVAL"
                elif btn == "√":
                    data = "SQRT("
                kb_row.append(InlineKeyboardButton(btn, callback_data=f"calc_{data}"))
            else:
                kb_row.append(InlineKeyboardButton(" ", callback_data="calc_IGNORE"))
        keyboard.append(kb_row)
    return InlineKeyboardMarkup(keyboard)

def process_calc_button(expr: str, data: str):
    """Process a single calculator button press."""
    if data == "CLEAR":
        return ""
    elif data == "EVAL":
        try:
            result = safe_eval(expr)
            return fmt(result)
        except:
            return "ERROR"
    elif data == "BACKSPACE":
        return expr[:-1]
    elif data == "SQRT(":
        return expr + "sqrt("
    elif data == "IGNORE":
        return expr
    else:
        return expr + data

def inlinecalc_message(expr, lang_dict):
    """Generate message text for inline calculator."""
    if expr == "":
        exp_str = lang_dict["inlinecalc_empty"]
    else:
        exp_str = expr
    title = lang_dict["inlinecalc_title"]
    expr_line = lang_dict["inlinecalc_expr"].format(expr=exp_str)
    try:
        res = fmt(safe_eval(expr))
        res_line = lang_dict["inlinecalc_result"].format(res=res)
    except:
        res_line = lang_dict["inlinecalc_error"]
    return f"{title}\n\n{expr_line}\n{res_line}"

# ==================== HANDLERS ====================
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    t = _(user)

    if chat.type == "private":
        save(chat.id, "private")
        add_btn = InlineKeyboardButton(t["add_btn"], url=f"https://t.me/{ctx.bot.username}?startgroup=true")
        if user.id in ADMIN_IDS:
            reply_kb = [["📊 All Users", "📢 Broadcast"]]
            await update.message.reply_text(
                t["start_admin"],
                reply_markup=ReplyKeyboardMarkup(reply_kb, resize_keyboard=True)
            )
            await update.message.reply_text(
                t["privacy_note"],
                reply_markup=InlineKeyboardMarkup([[add_btn]])
            )
        else:
            await update.message.reply_text(
                t["start_user"],
                reply_markup=InlineKeyboardMarkup([[add_btn]])
            )
    else:
        save(chat.id, "group")

async def inlinecal(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Launch inline calculator."""
    chat = update.effective_chat
    user = update.effective_user
    t = _(user)
    expr = ""
    msg = inlinecalc_message(expr, t)
    await update.message.reply_text(msg, reply_markup=build_calc_markup(expr))

async def calc_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    t = _(user)
    data = query.data.replace("calc_", "")
    # Get current expression from message text (parse between lines)
    current_text = query.message.text
    # We stored expression in message text as "<title>\n\nExpression: ...\nResult: ..."
    # Better: store expression in callback data? No, we have 64 char limit. We'll use the message text to extract expression.
    # The generated message has "Expression: <expr>" line. We'll parse it.
    lines = current_text.split("\n")
    expr_str = None
    for line in lines:
        # Look for line containing "Expression:" (English) or equivalent
        # Use detection of the key
        for lang_key in ["Expression:", "अभिव्यक्ति:", "Выражение:", "অভিব্যক্তি:"]:
            if line.startswith(lang_key):
                expr_str = line[len(lang_key):].strip()
                break
        if expr_str is not None:
            break
    if expr_str is None:
        expr = ""
    else:
        expr = expr_str.rstrip()
    if expr == t["inlinecalc_empty"]:
        expr = ""
    # Process
    new_expr = process_calc_button(expr, data)
    if new_expr == "ERROR":
        new_expr = expr  # keep old
        # show error
    new_msg = inlinecalc_message(new_expr, t)
    try:
        await query.edit_message_text(new_msg, reply_markup=build_calc_markup(new_expr))
    except Exception as e:
        logger.warning(f"Failed to edit inline calc: {e}")
    await query.answer()

# ==================== MESSAGE HANDLERS ====================
async def text_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user
    chat = update.effective_chat
    txt = msg.text.strip() if msg.text else ""
    t = _(user)

    save(chat.id, "private" if chat.type=="private" else "group")

    # Admin broadcast
    if user.id in ADMIN_IDS and chat.type=="private":
        state = ctx.user_data.get("state")
        if state == BROADCAST:
            await broadcast_send(update, ctx)
            ctx.user_data["state"] = None; return
        if txt == "📊 All Users":
            await msg.reply_text(t["all_users"].format(cnt=count_all())); return
        if txt == "📢 Broadcast":
            ctx.user_data["state"] = BROADCAST
            await msg.reply_text(t["broadcast_prompt"]); return
        if txt == "/cancel":
            ctx.user_data["state"] = None
            await msg.reply_text(t["broadcast_cancel"]); return

    # Auto calculator
    if chat.type=="group" or (chat.type=="private" and user.id not in ADMIN_IDS):
        if not (user.id in ADMIN_IDS and ctx.user_data.get("state")==BROADCAST):
            res = extract_math(txt)
            if res:
                await msg.reply_text(t["calc_result"].format(res=res))
            elif chat.type=="private":
                await msg.reply_text(t["not_math"])

async def media_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user = update.effective_user
    chat = update.effective_chat
    save(chat.id, "private" if chat.type=="private" else "group")
    if user.id in ADMIN_IDS and chat.type=="private" and ctx.user_data.get("state")==BROADCAST:
        await broadcast_send(update, ctx)
        ctx.user_data["state"] = None

async def broadcast_send(update, ctx):
    msg = update.message
    user = update.effective_user
    t = _(user)
    all_chats = get_all()
    ok, bad = 0, 0
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
    await msg.reply_text(t["broadcast_done"].format(ok=ok, bad=bad))

async def error_handler(update, ctx):
    logger.error(f"Update {update} caused error {ctx.error}")

# ==================== MAIN ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("inlinecal", inlinecal))
    app.add_handler(CallbackQueryHandler(calc_callback, pattern="^calc_"))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, lambda u,c: save(u.effective_chat.id,"group")))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_msg))
    media = filters.PHOTO|filters.VIDEO|filters.Document.ALL|filters.AUDIO|filters.VOICE|filters.Sticker.ALL
    app.add_handler(MessageHandler(media, media_msg))
    app.add_error_handler(error_handler)

    logger.info(f"🤖 Bot v{VERSION} running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
