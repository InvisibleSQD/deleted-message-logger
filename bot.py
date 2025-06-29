import os
from pyrogram import Client, filters
from pyrogram.types import Message

BOT_TOKEN = os.environ.get("BOT_TOKEN")
USER_ID = int(os.environ.get("USER_ID"))

app = Client(
    "deleted_logger_bot",
    bot_token=BOT_TOKEN,
    parse_mode="html",
)

# Сохраняем сообщения в памяти (для фото/видео нужен кеш)
message_store = {}

@app.on_message(filters.private & filters.incoming)
async def store_message(c, m: Message):
    message_store[m.message_id] = m

@app.on_deleted_messages()
async def on_deleted(c, messages):
    for msg in messages:
        if msg.chat.type == "private" and msg.from_user:
            if msg.from_user.id != USER_ID:
                continue
            orig = message_store.get(msg.message_id)
            if not orig:
                continue
            # Формируем уведомление
            await c.send_message(
                USER_ID,
                f"🗑 <b>Удалено сообщение</b> от <a href=\"tg://user?id={USER_ID}\">тебя</a>:\n"
            )
            if orig.text:
                await c.send_message(USER_ID, orig.text)
            if orig.photo:
                await orig.download(in_memory=True)
                await c.send_photo(USER_ID, orig.download())
            if orig.video:
                await c.send_video(USER_ID, orig.download())

            # Удаляем из хранилища
            del message_store[msg.message_id]

if __name__ == "__main__":
    app.run()
