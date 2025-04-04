from telegram import Bot

# Токен твоего бота
BOT_TOKEN = '7637885048:AAGhLGRYLQMaCYWwwWW8d_k1NVYJlnfyyJo'

# ID чата или username (можно получить после общения с ботом)
CHAT_ID = 'твой_чат_id'

bot = Bot(token=BOT_TOKEN)

# Пример: отправка сообщения
bot.send_message(chat_id=CHAT_ID, text="Привет! Новая новость на сайте!")
