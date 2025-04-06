import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from scripts_bd.db_methods import *

CONFIG = {
    'token': '7530398431:AAFnSCkcu4_XaeRJ7Cz3_RRZ2O-wfYERous',
    'base_url': 'https://ваш-сайт.ru',
    'channel_id': '@factosphera_bot'
}

# "База данных" пользователей

db = NewsDB()
user_db = db.all_users()
registered_users = [item[3] for item in user_db]


class UserState:
    def __init__(self):
        self.token = None
        self.is_authenticated = False
        self.subscription = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    user_state = UserState()

    # Проверяем, есть ли пользователь в базе данных
    for user in user_db:
        if user[3] == user_id:  # Проверяем telegram id (4-й элемент в списке)
            user_state.token = user[1].strip()  # Логин (удаляем лишние пробелы)
            user_state.is_authenticated = True
            user_state.subscription = int(user[2].strip())
            break

    # Сохраняем состояние пользователя в контексте
    context.user_data['user_state'] = user_state

    if user_state.is_authenticated:
        await show_authenticated_menu(update, user_state)
    else:
        await show_unauthenticated_menu(update)


async def show_unauthenticated_menu(update: Update) -> None:
    """Меню для неавторизованных пользователей"""
    keyboard = [
        [
            InlineKeyboardButton("🔗 Связать с аккаунтом", callback_data='link_account'),
            InlineKeyboardButton("📰 Последние новости", callback_data='get_news'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Добро пожаловать в новостной бот!\n\n"
        "Здесь вы можете получать свежие новости с нашего сайта. "
        "Для доступа к персонализированным подпискам, пожалуйста, свяжите бота с вашим аккаунтом.",
        reply_markup=reply_markup
    )


async def show_authenticated_menu(update: Update, user_state: UserState) -> None:
    """Меню для авторизованных пользователей"""
    if user_state.subscription != 0:
        keyboard = [
            [
                InlineKeyboardButton("❌ Отменить подписку", callback_data='unsubscribe'),
                InlineKeyboardButton("📰 Последние новости", callback_data='get_news'),
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("⚡ Быстрая подписка", callback_data='fast_sub'),
                InlineKeyboardButton("📅 Ежедневная сводка", callback_data='daily_digest'),
            ],
            [
                InlineKeyboardButton("🔙 Назад", callback_data='back'),
            ]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Добро пожаловать, авторизованный пользователь!\n\n"
        "Вы можете настроить получение новостей по вашему вкусу.",
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user_state = context.user_data['user_state']

    if query.data == 'link_account':
        await query.edit_message_text(
            text="🔑 Пожалуйста, введите ваш уникальный токен, который вы можете получить в личном кабинете на нашем сайте."
        )
        context.user_data['expecting_token'] = True
    elif query.data == 'get_news':
        await get_latest_news(update, context, user_state)
    elif query.data == 'fast_sub':
        user_state.subscription = 1
        user_db[user_id] = user_state
        await query.edit_message_text(text="✅ Вы подписались на мгновенные уведомления о новостях!")
        await show_authenticated_menu_from_query(update, user_state)
    elif query.data == 'daily_digest':
        user_state.subscription = 2
        user_db[user_id] = user_state
        await query.edit_message_text(text="✅ Вы подписались на ежедневную сводку новостей!")
        await show_authenticated_menu_from_query(update, user_state)
    elif query.data == 'unsubscribe':
        user_state.subscription = 0
        user_db[user_id] = user_state
        await query.edit_message_text(text="❌ Вы отменили все подписки на новости.")
        await show_authenticated_menu_from_query(update, user_state)
    elif query.data == 'back':
        await show_unauthenticated_menu_from_query(update)
    elif query.data == 'menu':
        print(user_state.is_authenticated)
        if user_state.is_authenticated:
            await show_authenticated_menu_from_query(update, user_state)
        else:
            await show_unauthenticated_menu_from_query(update)


async def show_authenticated_menu_from_query(update: Update, user_state: UserState) -> None:
    """Показывает меню для авторизованных пользователей из обработчика кнопок"""
    query = update.callback_query

    if user_state.subscription != 0:
        keyboard = [
            [
                InlineKeyboardButton("❌ Отменить подписку", callback_data='unsubscribe'),
                InlineKeyboardButton("📰 Последние новости", callback_data='get_news'),
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("⚡ Быстрая подписка", callback_data='fast_sub'),
                InlineKeyboardButton("📅 Ежедневная сводка", callback_data='daily_digest'),
            ],
            [
                InlineKeyboardButton("🔙 Назад", callback_data='back'),
            ]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="👋 Добро пожаловать, авторизованный пользователь!\n\n"
             "Вы можете настроить получение новостей по вашему вкусу.",
        reply_markup=reply_markup
    )


async def show_unauthenticated_menu_from_query(update: Update) -> None:
    """Показывает меню для неавторизованных пользователей из обработчика кнопок"""
    query = update.callback_query
    keyboard = [
        [
            InlineKeyboardButton("🔗 Связать с аккаунтом", callback_data='link_account'),
            InlineKeyboardButton("📰 Последние новости", callback_data='get_news'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="👋 Добро пожаловать в новостной бот!\n\n"
             "Здесь вы можете получать свежие новости с нашего сайта. "
             "Для доступа к персонализированным подпискам, пожалуйста, свяжите бота с вашим аккаунтом.",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений (привязка аккаунта по ключу)"""
    user_id = update.effective_user.id
    user_state = context.user_data['user_state']
    print(user_state)

    # Если бот ожидает токен
    if context.user_data.get('expecting_token', False):
        input_token = update.message.text.strip()  # Удаляем пробелы

        # Ищем пользователя в базе по ключу (формат: user_id + user_login)
        user_found = None
        for user in user_db:
            expected_token = f"{user[0]}{user[1].strip()}"  # user_id + login
            print(expected_token)
            print(input_token)
            if input_token == expected_token:
                user_found = user
                break

        # Если ключ верный
        if user_found:
            # Обновляем telegram_id в базе данных
            db.update_user_telegram_id(user_found[0], user_id)

            # Обновляем состояние пользователя
            user_state.token = user_id
            user_state.is_authenticated = True
            context.user_data['user_state'] = user_state  # Сохраняем изменения

            await update.message.reply_text(
                "✅ Аккаунт успешно привязан!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Меню", callback_data="menu")]])
            )
            await show_authenticated_menu(update, user_state)
        else:
            await update.message.reply_text(
                "❌ Неверный ключ. Проверьте правильность ввода или обратитесь в поддержку.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Меню", callback_data="menu")]])
            )

        context.user_data['expecting_token'] = False  # Сбрасываем ожидание токена

    else:
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки меню для навигации.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Меню", callback_data="menu")]])
        )


async def validate_token(token: str) -> bool:
    """Проверяет валидность токена (заглушка)"""
    # Реализуйте проверку токена с вашим API
    return len(token) == 32  # Пример проверки


async def get_latest_news(update: Update, context: ContextTypes.DEFAULT_TYPE, user_state: UserState) -> None:
    """Получает и отправляет последние новости"""
    query = update.callback_query

    news = await fetch_news_from_api(user_state.token if user_state.is_authenticated else None)

    keyboard = [
        [InlineKeyboardButton("📋 Меню", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(
            text=f"📰 Последние новости:\n\n{news}\n\nЧто дальше?",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text=f"📰 Последние новости:\n\n{news}\n\nЧто дальше?",
            reply_markup=reply_markup
        )


async def fetch_news_from_api(token: str = None) -> str:
    """Получает новости с API (заглушка)"""
    if token:
        return "1. Персонализированная новость 1\n2. Персонализированная новость 2"
    else:
        return "1. Общая новость 1\n2. Общая новость 2\n3. Общая новость 3"


async def send_daily_digest(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет ежедневную сводку"""
    user_id = context.job.user_id
    user_state = user_db.get(user_id, None)

    if user_state and user_state.daily_digest:
        news = await fetch_news_from_api(user_state.token)
        keyboard = [
            [InlineKeyboardButton("📋 Меню", callback_data='menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=user_id,
            text=f"🌅 Доброе утро! Ваша ежедневная сводка:\n\n{news}",
            reply_markup=reply_markup
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logging.error("Exception while handling an update:", exc_info=context.error)

    if update and update.effective_message:
        await update.effective_message.reply_text("😕 Произошла ошибка. Пожалуйста, попробуйте позже.")


def main() -> None:
    """Запуск бота"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    # Уменьшаем логи httpx
    logging.getLogger("httpx").setLevel(logging.WARNING)

    application = Application.builder().token(CONFIG['token']).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Обработчики кнопок
    application.add_handler(CallbackQueryHandler(button_handler))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Обработчик ошибок
    application.add_error_handler(error_handler)

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
