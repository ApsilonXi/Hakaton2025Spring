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

    def parse_news_item_science_rf(self):
        response = requests.get(self.source)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем все блоки с новостями
            articles = soup.find_all("div", class_="u-news-detail-page__text-content")
            self.text = str(articles)

    def clean_html(self):
        soup = BeautifulSoup(self.text, "html.parser")
        allowed_tags = {"b", "br", "img", "p", "a"}
        soup = BeautifulSoup(self.text, "html.parser")

        # Заменим нестандартный тег <img-wyz> на <img>
        for custom_img in soup.find_all("img-wyz"):
            img_tag = soup.new_tag("img")
            for attr, value in custom_img.attrs.items():
                # Удалим двоеточия из названий атрибутов (некорректны в HTML)
                attr = attr.replace(":", "")
                img_tag[attr] = value
            custom_img.replace_with(img_tag)

        for tag in soup.find_all(True):  # True = все теги
            if tag.name not in allowed_tags:
                tag.unwrap()  # удаляет сам тег, оставляя содержимое

        clean_text = str(soup).strip('[]')
        self.text = clean_text


'''x = News("news", "author", "date", "title",
         "https://наука.рф/news/samye-interesnye-otkrytiya-uchenykh-za-pervuyu-nedelyu-aprelya/")

x.parse_news_item_science_rf()
x.clean_html()
print(x.text)'''