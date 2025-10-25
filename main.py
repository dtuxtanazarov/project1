import sqlite3
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

DB_FILE = "messages.db"

# --- DATABASE funksiyalari ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY,
        title TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        user TEXT,
        text TEXT,
        FOREIGN KEY(chat_id) REFERENCES chats(id)
    )
    """)
    conn.commit()
    conn.close()


def save_message_to_db(chat_id, chat_title, user, text):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # guruhni yozib qo'yish (agar yo'q bo'lsa)
    cur.execute("INSERT OR IGNORE INTO chats (id, title) VALUES (?, ?)", (chat_id, chat_title))

    # xabarni saqlash
    cur.execute("INSERT INTO messages (chat_id, user, text) VALUES (?, ?, ?)",
                (chat_id, user, text))

    conn.commit()
    conn.close()


def search_messages(query, chat_id=None):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    q = f"%{query.lower()}%"
    if chat_id:  # faqat bitta guruh ichidan qidirish
        cur.execute("""
            SELECT user, text FROM messages
            WHERE chat_id = ? AND LOWER(text) LIKE ?
            ORDER BY id DESC LIMIT 10
        """, (chat_id, q))
    else:  # barcha guruhlardan qidirish
        cur.execute("""
            SELECT chats.title, messages.user, messages.text
            FROM messages
            JOIN chats ON chats.id = messages.chat_id
            WHERE LOWER(messages.text) LIKE ?
            ORDER BY messages.id DESC LIMIT 10
        """, (q,))
    results = cur.fetchall()
    conn.close()
    return results


# --- TELEGRAM HANDLERLAR ---
async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        chat = update.message.chat
        save_message_to_db(
            chat.id,
            chat.title if chat.title else f"Chat {chat.id}",
            update.message.from_user.full_name,
            update.message.text
        )


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Foydalanish: /search so‘z")
        return

    query = " ".join(context.args)

    if update.message.chat.type in ["group", "supergroup"]:
        results = search_messages(query, chat_id=update.message.chat_id)
        if not results:
            await update.message.reply_text("Hech narsa topilmadi 😔")
        else:
            reply = "\n\n".join([f"{user}: {text}" for user, text in results])
            await update.message.reply_text(f"🔎 Natijalar:\n\n{reply}")
    else:
        results = search_messages(query)
        if not results:
            await update.message.reply_text("Hech narsa topilmadi 😔")
        else:
            reply = "\n\n".join([f"[{chat}] {user}: {text}" for chat, user, text in results])
            await update.message.reply_text(f"🔎 Natijalar:\n\n{reply}")


def main():
    init_db()  # db yaratish

    app = Application.builder().token("TOKENINGIZNI_QO'YING").build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_message))
    app.add_handler(CommandHandler("search", search))

    app.run_polling()


if __name__ == "__main__":
    main()
