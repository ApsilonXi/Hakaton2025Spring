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

CONFIG = {
    'token': '7530398431:AAFnSCkcu4_XaeRJ7Cz3_RRZ2O-wfYERous',
    'base_url': 'https://ваш-сайт.ru',
    'channel_id': '@factosphera_bot'
}

# "База данных" пользователей
user_db = {}


class UserState:
    def __init__(self):
        self.token = None
        self.is_authenticated = False
        self.fast_subscription = False
        self.daily_digest = False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id

    if user_id not in user_db:
        user_db[user_id] = UserState()

    user_state = user_db[user_id]

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
    if user_state.fast_subscription or user_state.daily_digest:
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
    user_state = user_db.get(user_id, UserState())

    if query.data == 'link_account':
        await query.edit_message_text(
            text="🔑 Пожалуйста, введите ваш уникальный токен, который вы можете получить в личном кабинете на нашем сайте."
        )
        context.user_data['expecting_token'] = True
    elif query.data == 'get_news':
        await get_latest_news(update, context, user_state)
    elif query.data == 'fast_sub':
        user_state.fast_subscription = True
        user_db[user_id] = user_state
        await query.edit_message_text(text="✅ Вы подписались на мгновенные уведомления о новостях!")
        await show_authenticated_menu_from_query(update, user_state)
    elif query.data == 'daily_digest':
        user_state.daily_digest = True
        user_db[user_id] = user_state
        await query.edit_message_text(text="✅ Вы подписались на ежедневную сводку новостей!")
        await show_authenticated_menu_from_query(update, user_state)
    elif query.data == 'unsubscribe':
        user_state.fast_subscription = False
        user_state.daily_digest = False
        user_db[user_id] = user_state
        await query.edit_message_text(text="❌ Вы отменили все подписки на новости.")
        await show_authenticated_menu_from_query(update, user_state)
    elif query.data == 'back':
        await show_unauthenticated_menu_from_query(update)
    elif query.data == 'menu':
        if user_state.is_authenticated:
            await show_authenticated_menu_from_query(update, user_state)
        else:
            await show_unauthenticated_menu_from_query(update)


async def show_authenticated_menu_from_query(update: Update, user_state: UserState) -> None:
    """Показывает меню для авторизованных пользователей из обработчика кнопок"""
    query = update.callback_query

    if user_state.fast_subscription or user_state.daily_digest:
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
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    user_state = user_db.get(user_id, UserState())

    if context.user_data.get('expecting_token', False):
        token = update.message.text
        if await validate_token(token):
            user_state.token = token
            user_state.is_authenticated = True
            user_db[user_id] = user_state
            await update.message.reply_text("✅ Ваш аккаунт успешно связан!")
            await show_authenticated_menu(update, user_state)
        else:
            # Создаем клавиатуру с кнопкой "Меню"
            keyboard = [
                [InlineKeyboardButton("📋 Меню", callback_data='menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "❌ Неверный токен. Пожалуйста, попробуйте еще раз.",
                reply_markup=reply_markup
            )
        context.user_data['expecting_token'] = False
    else:
        await update.message.reply_text("Пожалуйста, используйте меню для взаимодействия с ботом.")


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
    logger.error("Exception while handling an update:", exc_info=context.error)

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
