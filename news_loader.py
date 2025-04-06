import threading
from db_methods import NewsDB

db = NewsDB()


def load_new():
    db.add_news_auto()
    threading.Timer(3600, load_new).start()


load_new()
