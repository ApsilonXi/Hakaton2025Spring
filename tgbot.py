import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import psycopg2
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class NewsNotifier:
    def __init__(self, token: str, db_params: dict, base_url: str):
        self.bot = Bot(token=token)
        self.db_params = db_params
        self.base_url = base_url  # Базовый URL вашего сайта
        self.conn = None
        
    def connect_db(self):
        """Подключение к базе данных"""
        try:
            self.conn = psycopg2.connect(**self.db_params)
            logger.info("Успешное подключение к базе данных")
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise

    def get_latest_news(self, hours: int = 24):
        """Получение свежих новостей за последние N часов"""
        try:
            cursor = self.conn.cursor()
            time_threshold = datetime.now() - timedelta(hours=hours)
            
            cursor.execute("""
                SELECT n.news_title, s.source_name, n.news_id 
                FROM news n
                JOIN source s ON n.sourceID = s.source_id
                WHERE n.date >= %s AND n.status = TRUE
                ORDER BY n.date DESC
                LIMIT 10;
                """, (time_threshold,))
            
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения новостей: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def format_news_message(self, news_item):
        """Форматирование сообщения о новости"""
        title, source, news_id = news_item
        return (
            "Возможно вам будет интересно:\n"
            f"<b>{title}</b>\n"
            f"<i>{source}</i>\n"
            f"{self.base_url}/news/{news_id}\n"
        )

    def send_news_to_channel(self, channel_id: str):
        """Отправка новостей в канал/чат"""
        try:
            self.connect_db()
            latest_news = self.get_latest_news()
            
            if not latest_news:
                logger.info("Нет новых новостей для отправки")
                return
            
            for news_item in latest_news:
                message = self.format_news_message(news_item)
                self.bot.send_message(
                    chat_id=channel_id,
                    text=message,
                    parse_mode='HTML'
                )
                logger.info(f"Отправлена новость: {news_item[0]}")
                
        except Exception as e:
            logger.error(f"Ошибка отправки новостей: {e}")
        finally:
            if self.conn:
                self.conn.close()

# Конфигурация
CONFIG = {
    'token': 'ВАШ_TELEGRAM_BOT_TOKEN',
    'db_params': {
        'dbname': 'ваша_база',
        'user': 'ваш_пользователь',
        'password': 'ваш_пароль',
        'host': 'ваш_хост'
    },
    'base_url': 'https://ваш-сайт.ru',
    'channel_id': '@ваш_канал'  # Или ID чата
}

def main():
    notifier = NewsNotifier(
        token=CONFIG['token'],
        db_params=CONFIG['db_params'],
        base_url=CONFIG['base_url']
    )
    
    # Отправляем новости
    notifier.send_news_to_channel(CONFIG['channel_id'])

if __name__ == '__main__':
    main()