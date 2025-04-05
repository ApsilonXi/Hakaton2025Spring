import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from typing import Optional, List, Dict
import hashlib
import uuid


class NewsDB:
    def __init__(self, dbname='news_db', user='postgres', password='12345', host='localhost'):
        """Инициализация подключения к базе данных
           :return: None"""
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        self.conn.autocommit = True
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)

    def __del__(self):
        """Закрытие подключения при уничтожении объекта
           :return: None"""
        self.cursor.close()
        self.conn.close()
    
    def _get_user_role(self, user_id: int) -> Optional[str]:
        """Получение роли пользователя
           :return: роль пользователя или None если пользователь не найден"""
        self.cursor.execute("SELECT user_role FROM users WHERE id = %s", (user_id,))
        result = self.cursor.fetchone()
        return result['user_role'] if result else None

    def _check_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором
           :return: True если пользователь администратор, иначе False"""
        role = self._get_user_role(user_id)
        return role == 'admin'

    def _check_verified(self, user_id: int) -> bool:
        """Проверка, является ли пользователь верифицированным
           :return: True если пользователь верифицирован или администратор, иначе False"""
        role = self._get_user_role(user_id)
        return role in ('verified', 'admin')

    # Методы для работы с пользователями
    def register_user(self, login: str, password: str) -> Optional[int]:
        """Регистрация нового пользователя с использованием функции register_user
           :return: ID нового пользователя или None если регистрация не удалась"""
        try:
            self.cursor.execute(
                "SELECT register_user(%s, %s) AS result",
                (login, password)
            )
            self.cursor.execute(
                "SELECT id FROM users WHERE user_login = %s",
                (login,)
            )
            return self.cursor.fetchone()['id']
        except psycopg2.IntegrityError:
            return None

    def authenticate_user(self, login: str, password: str) -> Optional[Dict]:
        """Аутентификация пользователя с использованием функции authenticate_user
           :return: словарь с данными пользователя (id, login, role) или None если аутентификация не удалась"""
        self.cursor.execute(
            "SELECT authenticate_user(%s, %s) AS auth_result",
            (login, password)
        )
        auth_result = self.cursor.fetchone()['auth_result']
        
        if not auth_result:
            return None
        
        self.cursor.execute(
            "SELECT id, user_login, user_role FROM users WHERE user_login = %s",
            (login,)
        )
        user = self.cursor.fetchone()
        
        return {
            'id': user['id'],
            'login': user['user_login'].strip(),
            'role': user['user_role'].strip()
        }
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Смена пароля пользователя с использованием SQL-функций
        :return: True если пароль успешно изменен, иначе False"""
        
        # 1. Проверяем старый пароль
        self.cursor.execute(
            "SELECT authenticate_user(user_login, %s) AS auth_result FROM users WHERE id = %s",
            (old_password, user_id)
        )
        result = self.cursor.fetchone()
        
        if not result or not result['auth_result']:
            return False
        
        # 2. Хешируем новый пароль с помощью SQL-функции crypt
        self.cursor.execute(
            "SELECT crypt(%s, gen_salt('bf')) AS new_hash",
            (new_password,)
        )
        new_hash = self.cursor.fetchone()['new_hash']
        
        # 3. Обновляем пароль в базе
        self.cursor.execute(
            "UPDATE users SET user_password = %s WHERE id = %s",
            (new_hash, user_id)
        )
        return True
    
    def update_user_telegram_id(self, user_id: int, telegram_id: int) -> bool:
        """Обновление telegram_id пользователя с хешированием
        :param user_id: ID пользователя
        :param telegram_id: Telegram ID пользователя
        :return: True если обновление успешно, иначе False"""
        
        # Проверяем существование пользователя
        self.cursor.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
        if not self.cursor.fetchone():
            return False
        
        # Хешируем telegram_id с помощью SHA-256
        hashed_telegram_id = hashlib.sha256(str(telegram_id).encode()).hexdigest()
        
        self.cursor.execute(
            "UPDATE users SET telegram_id = %s WHERE id = %s",
            (hashed_telegram_id, user_id)
        )
        return self.cursor.rowcount > 0
    
    def verify_telegram_id(self, user_id: int, telegram_id: int) -> bool:
        """Проверка соответствия telegram_id пользователю
        :param user_id: ID пользователя
        :param telegram_id: Telegram ID для проверки
        :return: True если telegram_id соответствует, иначе False"""
        
        self.cursor.execute(
            "SELECT telegram_id FROM users WHERE id = %s",
            (user_id,)
        )
        result = self.cursor.fetchone()
        
        if not result or not result['telegram_id']:
            return False
        
        # Хешируем предоставленный telegram_id для сравнения
        hashed_input = hashlib.sha256(str(telegram_id).encode()).hexdigest()
        
        return hashed_input == result['telegram_id']

    def upgrade_to_verified(self, admin_id: int, user_id: int) -> bool:
        """Повышение пользователя до верифицированного (админом)
           :return: True если обновление успешно, иначе False"""
        if not self._check_admin(admin_id):
            return False

        self.cursor.execute(
            "UPDATE users SET user_role = 'verified' WHERE id = %s",
            (user_id,)
        )
        return self.cursor.rowcount > 0

    def set_notification_preference(self, user_id: int, preference: str) -> bool:
        """Установка предпочтений уведомлений
           :return: True если настройки успешно обновлены, иначе False"""
        self.cursor.execute(
            "UPDATE users SET notification = %s WHERE id = %s",
            (preference, user_id)
        )
        return self.cursor.rowcount > 0

    def update_subscriptions(self, user_id: int, tag_id: Optional[int] = None, source_id: Optional[int] = None) -> bool:
        """Обновление подписок пользователя
           :return: True если подписки успешно обновлены, иначе False"""
        updates = []
        params = []

        if tag_id is not None:
            updates.append("tag_subscription = %s")
            params.append(tag_id)

        if source_id is not None:
            updates.append("sources_subsc = %s")
            params.append(source_id)

        if not updates:
            return False

        params.append(user_id)
        query = sql.SQL("UPDATE users SET {} WHERE id = %s").format(
            sql.SQL(", ").join(map(sql.SQL, updates))
        )
        self.cursor.execute(query, params)
        return self.cursor.rowcount > 0
    
    def all_users(self):
        '''Получение всех пользователей БД
           :return: список всех пользователей с их ID, логинами и настройками уведомлений'''
        self.cursor.execute("""
            SELECT id, user_login, notification FROM users; 
            """)
        return self.cursor.fetchall()

    # Методы для работы с новостями
    def add_news(self, user_id: int, title: str, content: str, tag_id: Optional[int] = None, 
                source_id: Optional[int] = None, is_organization: bool = False) -> Optional[int]:
        """Добавление новости:
           - Для верифицированных и админов: сразу публикуется (status=True)
           - Для обычных: на модерацию (status=False)
           :return: ID добавленной новости или None если добавление не удалось"""
        role = self._get_user_role(user_id)
        if role is None:
            return None

        status = role in ('verified', 'admin')

        self.cursor.execute(
            """INSERT INTO news (title, content, status, tag, source, type_news)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (title, content, status, tag_id, source_id, not is_organization)
        )
        news_id = self.cursor.fetchone()['id']
        
        if tag_id:
            self.add_tag_to_news(user_id, news_id, tag_id)

        return news_id

    def get_published_news(self, tag_id: Optional[int] = None, source_id: Optional[int] = None) -> List[Dict]:
        """Получение опубликованных новостей с информацией об источниках и тегах
        :return: список словарей с данными новостей, включая название источника, ссылку и теги"""
        # Основной запрос для получения новостей
        query = """
            SELECT 
                n.id,
                n.type_news,
                n.title,
                n.content,
                n.status,
                n.source,
                n.date,
                s.name as source_name, 
                s.link as source_link,
                ARRAY_AGG(t.name) as tags
            FROM news n
            LEFT JOIN sources s ON n.source = s.id
            LEFT JOIN tags_news tn ON n.id = tn.newsid
            LEFT JOIN tags t ON tn.tagid = t.id
            WHERE n.status = TRUE
            GROUP BY n.id, s.name, s.link
        """
        params = []

        if tag_id is not None:
            query = query.replace("GROUP BY", "AND t.id = %s GROUP BY")
            params.append(tag_id)

        if source_id is not None:
            query = query.replace("GROUP BY", "AND n.source = %s GROUP BY")
            params.append(source_id)

        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_news_for_moderation(self, admin_id: int) -> List[Dict]:
        """Получение новостей для модерации (админом)
           :return: список словарей с новостями для модерации или пустой список если пользователь не админ"""
        if not self._check_admin(admin_id):
            return []

        self.cursor.execute("SELECT * FROM news WHERE status = FALSE")
        return [dict(row) for row in self.cursor.fetchall()]

    def approve_news(self, admin_id: int, news_id: int) -> bool:
        """Одобрение новости (админом)
           :return: True если новость успешно одобрена, иначе False"""
        if not self._check_admin(admin_id):
            return False

        self.cursor.execute(
            "UPDATE news SET status = TRUE WHERE id = %s",
            (news_id,)
        )
        return self.cursor.rowcount > 0

    def reject_news(self, admin_id: int, news_id: int) -> bool:
        """Отклонение новости (админом)
           :return: True если новость успешно отклонена, иначе False"""
        if not self._check_admin(admin_id):
            return False

        self.cursor.execute("DELETE FROM news WHERE id = %s AND status = FALSE", (news_id,))
        return self.cursor.rowcount > 0

    # Методы для работы с тегами
    def add_tag(self, name: str) -> Optional[int]:
        """Добавление нового тега
           :return: ID добавленного тега или None если тег уже существует"""
        try:
            self.cursor.execute(
                "INSERT INTO tags (name) VALUES (%s) RETURNING id",
                (name,)
            )
            return self.cursor.fetchone()['id']
        except psycopg2.IntegrityError:
            return None

    def get_all_tags(self) -> List[Dict]:
        """Получение списка всех тегов
           :return: список словарей с данными тегов"""
        self.cursor.execute("SELECT * FROM tags")
        return [dict(row) for row in self.cursor.fetchall()]

    def add_tag_to_news(self, user_id: int, news_id: int, tag_id: int) -> bool:
        """Добавление тега к новости
           :return: True если тег успешно добавлен, иначе False"""
        if not (self._check_admin(user_id) or self._check_verified(user_id)):
            return False

        try:
            self.cursor.execute(
                "INSERT INTO tags_news (tagID, newsID) VALUES (%s, %s)",
                (tag_id, news_id)
            )
            return True
        except psycopg2.IntegrityError:
            return False

    # Методы для работы с источниками
    def add_source(self, name: str, link: str) -> Optional[int]:
        """Добавление нового источника
           :return: ID добавленного источника или None если источник уже существует"""
        try:
            self.cursor.execute(
                "INSERT INTO sources (name, link) VALUES (%s, %s) RETURNING id",
                (name, link)
            )
            return self.cursor.fetchone()['id']
        except psycopg2.IntegrityError:
            return None

    def get_all_sources(self) -> List[Dict]:
        """Получение списка всех источников
           :return: список словарей с данными источников"""
        self.cursor.execute("SELECT * FROM sources")
        return [dict(row) for row in self.cursor.fetchall()]

    # Методы для работы с папками
    def create_folder(self, user_id: int, folder_name: str) -> Optional[int]:
        """Создание папки для пользователя
           :return: ID созданной папки или None если создание не удалось"""
        self.cursor.execute(
            "SELECT user_login FROM users WHERE id = %s",
            (user_id,)
        )
        user = self.cursor.fetchone()
        if not user:
            return None

        try:
            self.cursor.execute(
                "INSERT INTO folders (userLOG, name) VALUES (%s, %s) RETURNING id",
                (user['user_login'], folder_name)
            )
            return self.cursor.fetchone()['id']
        except psycopg2.IntegrityError:
            return None

    def add_news_to_folder(self, user_id: int, folder_id: int, news_id: int) -> bool:
        """Добавление новости в папку
           :return: True если новость успешно добавлена, иначе False"""
        self.cursor.execute(
            """SELECT 1 FROM folders f
               JOIN users u ON f.userLOG = u.user_login
               WHERE f.id = %s AND u.id = %s""",
            (folder_id, user_id)
        )
        if not self.cursor.fetchone():
            return False

        self.cursor.execute(
            "UPDATE folders SET newsID = %s WHERE id = %s",
            (news_id, folder_id)
        )
        return self.cursor.rowcount > 0

    def get_user_folders(self, user_id: int) -> List[Dict]:
        """Получение папок пользователя
           :return: список словарей с данными папок пользователя"""
        self.cursor.execute(
            """SELECT f.id, f.name, f.newsID 
               FROM folders f
               JOIN users u ON f.userLOG = u.user_login
               WHERE u.id = %s""",
            (user_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def suggest_news_source(self, user_id: int, link: str) -> bool:
        """Отправка предложения нового источника
           :return: True если предложение успешно сохранено, иначе False"""
        self.cursor.execute(
            "UPDATE users SET notification = %s WHERE id = %s",
            (f"source_suggestion:{link}", user_id)
        )
        return self.cursor.rowcount > 0

    def update_user_telegram_id(self, user_id: int, telegram_id: int):
        self.cursor.execute(
            "UPDATE users SET telegram_id = %s WHERE id = %s",
            (telegram_id, user_id)
        )
        return self.cursor.rowcount > 0
