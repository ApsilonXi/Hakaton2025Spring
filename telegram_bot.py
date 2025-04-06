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

import datetime
from db_methods import *

CONFIG = {
    'token': '7530398431:AAFnSCkcu4_XaeRJ7Cz3_RRZ2O-wfYERous',
    'base_url': 'https://ваш-сайт.ru',
    'channel_id': '@factosphera_bot'
}

# "База данных" пользователей

db = NewsDB()
user_db = db.all_users()



class UserState:
    def __init__(self):
        self.id = None
        self.token = None
        self.is_authenticated = False
        self.subscription = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    user_state = UserState()

    # Проверяем, есть ли пользователь в базе данных
    for user in user_db:
        if user['telegram_id'] == user_id:  # Проверяем telegram id (4-й элемент в списке)
            user_state.id = user['id']
            user_state.token = user['user_login'].strip()  # Логин (удаляем лишние пробелы)
            user_state.is_authenticated = True
            user_state.subscription = int(user['telegram_id'].strip())
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
        "👋 Фактосфера на связи!\n\n"
        "Свежие новости науки, с нашего сайта, теперь у вас чате. "
        "Для доступа к персонализированным подпискам, пожалуйста, свяжите бота с вашим аккаунтом.",
        reply_markup=reply_markup
    )


async def show_authenticated_menu(update: Update, user_state: UserState, special_mode=None) -> None:
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
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if special_mode == 'authorized':
        await update.message.reply_text(
            "👋 Авторизация прошла успешно!\n\n"
            "Вы можете настроить получение новостей по вашему вкусу.",
            reply_markup=reply_markup
        )
    elif user_state.subscription == 0:
        await update.message.reply_text(
            "👋 Добро пожаловать, авторизованный пользователь!\n\n"
            "Вы можете настроить получение новостей по вашему вкусу.\n\n"
            "Быстрая подписка позволит получать актуальные новости одновременно с публикацией на нашем сайте.\n"
            "Ежедневная сводка, сформирует утренние подборки актуальных новостей на основе ваших подписок.",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "👋 Добро пожаловать, авторизованный пользователь!\n\n"
            "Желаете получить сводку актуальных новостей или отменить подписку на уведомления?",
            reply_markup=reply_markup
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопок"""
    query = update.callback_query
    await query.answer()

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
        context.user_data['user_state'] = user_state
        db.update_subscribe(user_state.id, '1')
        await show_authenticated_menu_from_query(update, user_state, "subscribe")
    elif query.data == 'daily_digest':
        user_state.subscription = 2
        context.user_data['user_state'] = user_state
        db.update_subscribe(user_state.id, '2')
        await show_authenticated_menu_from_query(update, user_state, "subscribe")
    elif query.data == 'unsubscribe':
        user_state.subscription = 0
        user_state.is_authenticated = False
        db.update_user_telegram_id(user_state.id, 1000000000)
        db.update_subscribe(user_state.id, "0")
        context.user_data['user_state'] = user_state
        await show_unauthenticated_menu_from_query(update)
    elif query.data == 'menu':
        if user_state.is_authenticated:
            await show_authenticated_menu_from_query(update, user_state)
        else:
            await show_unauthenticated_menu_from_query(update)


async def show_authenticated_menu_from_query(update: Update, user_state: UserState, special_mode=None) -> None:
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
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if special_mode == "subscribe":
        await query.edit_message_text(
            text="👋 Подписка успешно применена!\n\n"
                 "Новые уведомления скоро поступят",
            reply_markup=reply_markup
        )
    else:
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

    # Если бот ожидает токен
    if context.user_data.get('expecting_token', False):
        input_token = update.message.text.strip()  # Удаляем пробелы

        # Ищем пользователя в базе по ключу (формат: user_id + user_login)
        user_found = None
        for user in user_db:
            expected_token = f"{user['id']}{user['user_login'].strip()}"  # user_id + login
            if input_token == expected_token:
                user_found = user
                break

        # Если ключ верный
        if user_found:
            # Обновляем telegram_id в базе данных
            db.update_user_telegram_id(user_found[0], user_id)

            # Обновляем состояние пользователя
            user_state.token = user_id
            user_state.id = user_found[0]
            user_state.is_authenticated = True
            context.user_data['user_state'] = user_state  # Сохраняем изменения
            await show_authenticated_menu(update, user_state, 'authorized')
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


async def get_latest_news(update: Update, context: ContextTypes.DEFAULT_TYPE, user_state: UserState) -> None:
    """Получает и отправляет последние новости"""
    query = update.callback_query
    news_list = db.get_published_news()
    cut_list = news_list[:10]

    news = ''

    for count, item in enumerate(cut_list):
        news += f'{count + 1}. {item['title']}\n{item['link']}\n\n'

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


async def fetch_news_from_api(news: List[dict], user_id: int = None) -> str:
    """Получает новости с API (заглушка)"""
    if user_id:
        user_tags = db.get_by_user_id(user_id)
        print(f"Теги юзеров {user_tags}")

    return 'Здесь будут ваши новости! Как только они появятся...'


async def daily_digest(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет ежедневную сводку"""

    users = db.all_users()
    news = db.get_published_news()
    print(news)
    print(users)

    for user in users:
        if user[2].strip() == '2' and user[3] != 1000000000:
            try:
                news = await fetch_news_from_api(news, user[0])
                await context.bot.send_message(
                    chat_id=user[3],
                    text=f"🌅 Доброе утро! Ваша ежедневная сводка:\n\n{news}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📋 Меню", callback_data="menu")]
                    ])
                )
            except Exception as e:
                logging.error(f"Ошибка отправки дайджеста для {user[0]}: {e}")


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

    job_queue = application.job_queue

    '''application.job_queue.run_once(
        daily_digest,
        when=10,
        chat_id=1333624885  # Укажите реальный chat_id
    )'''

    # Теперь можно настраивать задачи
    job_queue.run_daily(
        daily_digest,
        time=datetime.time(hour=11, minute=0),
        days=(0, 1, 2, 3, 4, 5, 6)
    )

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
