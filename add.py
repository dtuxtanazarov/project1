#git fetch uchun yangi o`zgarishlar
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# Xabarlarni saqlash (oddiy ro'yxat)
messages_db = []


# Guruhdan kelayotgan xabarlarni yig'ish
async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        messages_db.append({
            "user": update.message.from_user.full_name,
            "text": update.message.text,
            "id": update.message.message_id
        })


# Qidiruv funksiyasi
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Foydalanish: /search so‘z")
        return

    query = " ".join(context.args).lower()
    results = [m for m in messages_db if query in m["text"].lower()]

    if not results:
        await update.message.reply_text("Hech narsa topilmadi 😔")
    else:
        reply = "\n\n".join([f"{m['user']}: {m['text']}" for m in results[-10:]])  # oxirgi 10 ta
        await update.message.reply_text(f"🔎 Natijalar:\n\n{reply}")


def main():
    app = Application.builder().token("BOT_TOKENINGIZ").build()

    # Guruhdagi xabarlarni yig‘ish
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_message))

    # Qidiruv komandasi
    app.add_handler(CommandHandler("search", search))

    app.run_polling()


if __name__ == "__main__":
    main()
