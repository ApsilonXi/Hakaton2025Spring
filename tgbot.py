import logging
from telegram import Bot
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

CONFIG = {
    'token': '7530398431:AAFnSCkcu4_XaeRJ7Cz3_RRZ2O-wfYERous',
    'base_url': 'https://ваш-сайт.ru',
    'channel_id': '@factosphera_bot'  
}

class NewsNotifier:
    def __init__(self, connection):
        self.bot = Bot(token=CONFIG['token'])
        self.conn = connection
        self.base_url = CONFIG['base_url']  

    def start_bot(self):
        notifier = NewsNotifier(
            token=CONFIG['token'],
            base_url=CONFIG['base_url']
        )
        notifier.send_news_to_channel(CONFIG['channel_id'])

    def get_latest_news(self, hours: int = 4):
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


