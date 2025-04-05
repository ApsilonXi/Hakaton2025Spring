import requests
from bs4 import BeautifulSoup


class News:
    def __init__(self, news_type, author, date, title, source):
        """
        Класс "Новость"
        :param news_type: Тип новости
        :param author: Автор (сайт откуда новость загружена)
        :param date: Дата публикации
        :param title: Заголовок
        :param source: Ссылка на оригинальную новость
        """
        self.news_type = news_type
        self.author = author
        self.date = date
        self.title = title
        self.source = source
        self.text = None
        self.tags = []

    def parse_news_item(self):
        response = requests.get(self.source)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем все блоки с новостями
            articles = soup.find_all("div", class_="u-news-detail-page__text-content")
            print(articles)


x = News("news", "author", "date", "title",
         "https://наука.рф/news/samye-interesnye-otkrytiya-uchenykh-za-pervuyu-nedelyu-aprelya/")

x.parse_news_item()
