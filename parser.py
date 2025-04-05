from class_News import News
import requests
from bs4 import BeautifulSoup


def parse_science_rf():
    """
    Функция обработки сайта наука.рф
    :return:
    """
    # Отправляем GET-запрос на сайт
    url = "https://наука.рф/news/"
    response = requests.get(url)
    news_list = []

    # Проверяем успешность запроса
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем все блоки с новостями
        articles = soup.find_all("a", class_="news-item g-blur-bg")
        print(len(articles))

        for article in articles:
            # Извлекаем href (ссылку) из атрибута <a>
            link = article["href"]
            full_link = "https://наука.рф" + link  # Добавляем базовый URL, если ссылка относительная
            date = article.find("div", class_="news-item__date").text.strip()
            title = article.find("div", class_="news-item__title").text.strip()
            author = "наука.рф"

            news_list.append(News("news", author, date, title, full_link))

    else:
        print("Ошибка загрузки страницы. Код ответа:", response.status_code)

    return news_list
