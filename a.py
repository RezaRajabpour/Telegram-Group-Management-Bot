import os
import json
from datetime import datetime, timedelta
from telegram import ChatPermissions, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

TOKEN = ""
WARNINGS_FILE = "warning.json"
BANNED_WORDS_FILE = "a.txt"

try:
    with open(BANNED_WORDS_FILE, "r", encoding="utf-8") as f:
        BANNED_WORDS = {line.strip().lower() for line in f if line.strip()}
except FileNotFoundError:
    BANNED_WORDS = set()

def load_warnings():
    if not os.path.exists(WARNINGS_FILE) or os.path.getsize(WARNINGS_FILE) == 0:
        return {}
    with open(WARNINGS_FILE, "r", encoding="utf-8") as f1:
        try:
            return json.load(f1)
        except json.JSONDecodeError:
            return {}

def save_warnings(data):
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f2:
        json.dump(data, f2, indent=2, ensure_ascii=False)

async def mute_user(context, chat_id, user_id, hours=24):
    await context.bot.restrict_chat_member(
        chat_id, user_id,
        ChatPermissions(can_send_messages=False),
        until_date=datetime.now().astimezone() + timedelta(hours=hours)
    )

async def clear_user_warnings(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    chat_id = job_data["chat_id"]
    user_id = job_data["user_id"]
    key = f"{chat_id}_{user_id}"
    warnings_data = load_warnings()
    if key in warnings_data:
        warnings_data.pop(key)
        save_warnings(warnings_data)
        try:
            await context.bot.send_message(chat_id, f"✅ اخطارهای کاربر [id:{user_id}](tg://user?id={user_id}) پاک شد.", parse_mode="Markdown")
        except:
            pass

async def check_message(update, context):
    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    user = update.effective_user
    chat_id = update.effective_chat.id
    user_id = user.id
    username = user.username or user.first_name
    message_text = update.message.text.lower()
    warnings_data = load_warnings()
    key = f"{chat_id}_{user_id}"

    matched_word = next((word for word in BANNED_WORDS if word in message_text), None)
    if matched_word:
        warning_info = warnings_data.get(key, {"count": 0, "warnings": []})

        if warning_info.get("count", 0) == 0:
            warning_info["first_warning_time"] = datetime.now().astimezone().isoformat()
            context.job_queue.run_once(
                clear_user_warnings,
                when=timedelta(hours=24),
                data={"chat_id": chat_id, "user_id": user_id},
                name=f"clear_{chat_id}_{user_id}"
            )

        warning_info.setdefault("warnings", []).append({
            "time": datetime.now().astimezone().isoformat(),
            "word": matched_word,
            "username": username
        })
        warning_info["count"] = warning_info.get("count", 0) + 1
        warnings_data[key] = warning_info
        save_warnings(warnings_data)

        if warning_info["count"] < 3:
            await update.message.reply_text(
                f"⚠️ اخطار برای {username}\n<b>اخطار {warning_info['count']} از ۳</b>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                f"🚫 {username}، شما ۳ اخطار دریافت کردید و به مدت ۲۴ ساعت بی‌صدا شدید.",
                parse_mode="HTML"
            )
            await mute_user(context, chat_id, user_id, hours=24)
            warnings_data[key] = {"count": 0, "warnings": []}
            save_warnings(warnings_data)

async def lock_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.set_chat_permissions(
        chat_id,
        ChatPermissions(can_send_messages=False)
    )
    await update.message.reply_text("🔒 گروه قفل شد، هیچکس نمی‌تواند پیام ارسال کند.")

async def unlock_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.set_chat_permissions(
        chat_id,
        ChatPermissions(can_send_messages=True)
    )
    await update.message.reply_text("🔓 گروه باز شد، اعضا می‌توانند دوباره پیام بدهند.")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))
    app.add_handler(CommandHandler("lock", lock_group))
    app.add_handler(CommandHandler("unlock", unlock_group))
    app.run_polling()
