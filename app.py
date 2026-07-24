
import os
import handlers
from aiogram import executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from data import config
from loader import dp, db, bot
import filters
import logging

filters.setup(dp)

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))
user_message = "👤 Użytkownik"
admin_message = "👑 Admin"


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(user_message, admin_message)

    await message.answer('''Cześć! 🤖 Witaj w moim sklepie automatycznym. 

Wybierz interesującą Cię kategorię z menu poniżej, aby złożyć zamówienie i natychmiast otrzymać swój produkt cyfrowy.

W razie pytań użyj komendy /sos, aby skontaktować się z administratorem.''', reply_markup=markup)
    ''', reply_markup=markup)


@dp.message_handler(text=user_message)
async def user_mode(message: types.Message):

    cid = message.chat.id
    if cid in config.ADMINS:
        config.ADMINS.remove(cid)

    await message.answer('Uruchomiono tryb użytkownika.', reply_markup=ReplyKeyboardRemove())

@dp.message_handler(text=admin_message)
async def admin_mode(message: types.Message):

    cid = message.chat.id
    if cid not in config.ADMINS:
        config.ADMINS.append(cid)

    await message.answer('Uruchomiono tryb użytkownika.', reply_markup=ReplyKeyboardRemove())

async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)
    db.create_tables()

    await bot.delete_webhook()
    if config.WEBHOOK_URL:
        await bot.set_webhook(config.WEBHOOK_URL)


async def on_shutdown():
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")

import os
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

def run_dummy_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

Thread(target=run_dummy_server, daemon=True).start()
if __name__ == '__main__':

    if (("HEROKU_APP_NAME" in list(os.environ.keys())) or
        ("RAILWAY_PUBLIC_DOMAIN" in list(os.environ.keys()))):

        executor.start_webhook(
            dispatcher=dp,
            webhook_path=config.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )

    else:

        executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
