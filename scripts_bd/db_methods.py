import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from typing import Optional, List, Dict, Union
import hashlib
import uuid

class NewsDB:
    def __init__(self, dbname='news_db', user='postgres', password='12345', host='localhost'):
        """Инициализация подключения к базе данных"""
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        self.conn.autocommit = True
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)
    
    def __del__(self):
        """Закрытие подключения при уничтожении объекта"""
        self.cursor.close()
        self.conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        salt = uuid.uuid4().hex
        return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
    
    def _check_password(self, hashed_password: str, user_password: str) -> bool:
        """Проверка пароля"""
        password, salt = hashed_password.split(':')
        return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
    
    def _get_user_role(self, user_id: int) -> Optional[str]:
        """Получение роли пользователя"""
        self.cursor.execute("SELECT user_role FROM users WHERE id = %s", (user_id,))
        result = self.cursor.fetchone()
        return result['user_role'] if result else None
    
    def _check_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        role = self._get_user_role(user_id)
        return role == 'admin'
    
    def _check_verified(self, user_id: int) -> bool:
        """Проверка, является ли пользователь верифицированным"""
        role = self._get_user_role(user_id)
        return role in ('verified', 'admin')

    # Методы для работы с пользователями
    def register_user(self, login: str, password: str) -> Optional[int]:
        """Регистрация нового пользователя"""
        try:
            hashed_password = self._hash_password(password)
            self.cursor.execute(
                "INSERT INTO users (user_login, user_password, user_role) VALUES (%s, %s, 'user') RETURNING id",
                (login, hashed_password)
            )
            return self.cursor.fetchone()['id']
        except psycopg2.IntegrityError:
            return None
    
    def authenticate_user(self, login: str, password: str) -> Optional[Dict]:
        """Аутентификация пользователя"""
        self.cursor.execute(
            "SELECT id, user_password, user_role FROM users WHERE user_login = %s",
            (login,)
        )
        user = self.cursor.fetchone()
        
        if user and self._check_password(user['user_password'], password):
            return {
                'id': user['id'],
                'login': login,
                'role': user['user_role']
            }
        return None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Смена пароля пользователя"""
        self.cursor.execute(
            "SELECT user_password FROM users WHERE id = %s",
            (user_id,)
        )
        result = self.cursor.fetchone()
        
        if not result or not self._check_password(result['user_password'], old_password):
            return False
        
        new_hashed_password = self._hash_password(new_password)
        self.cursor.execute(
            "UPDATE users SET user_password = %s WHERE id = %s",
            (new_hashed_password, user_id)
        )
        return True
    
    def upgrade_to_verified(self, admin_id: int, user_id: int) -> bool:
        """Повышение пользователя до верифицированного (админом)"""
        if not self._check_admin(admin_id):
            return False
        
        self.cursor.execute(
            "UPDATE users SET user_role = 'verified' WHERE id = %s",
            (user_id,)
        )
        return self.cursor.rowcount > 0
    
    def set_notification_preference(self, user_id: int, preference: str) -> bool:
        """Установка предпочтений уведомлений"""
        self.cursor.execute(
            "UPDATE users SET notification = %s WHERE id = %s",
            (preference, user_id)
        )
        return self.cursor.rowcount > 0
    
    def update_subscriptions(self, user_id: int, tag_id: Optional[int] = None, source_id: Optional[int] = None) -> bool:
        """Обновление подписок пользователя"""
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
        '''Получение всех пользователей БД'''
        self.cursor.execute("""
            SELECT id FROM users; 
            """)
        return self.cursor.fetchall()
    
    # Методы для работы с новостями
    def add_news(self, user_id: int, title: str, content: str, tag_id: Optional[int] = None, 
                source_id: Optional[int] = None, is_organization: bool = False) -> Optional[int]:
        """
        Добавление новости:
        - Для верифицированных и админов: сразу публикуется (status=True)
        - Для обычных: на модерацию (status=False)
        """
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
        
        # Если указан тег, создаем связь в tags_news
        if tag_id:
            self.add_tag_to_news(user_id, news_id, tag_id)
        
        return news_id
    
    def get_published_news(self, tag_id: Optional[int] = None, source_id: Optional[int] = None) -> List[Dict]:
        """Получение опубликованных новостей"""
        query = "SELECT * FROM news WHERE status = TRUE"
        params = []
        
        if tag_id is not None:
            query += " AND id IN (SELECT newsID FROM tags_news WHERE tagID = %s)"
            params.append(tag_id)
        
        if source_id is not None:
            query += " AND source = %s"
            params.append(source_id)
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_news_for_moderation(self, admin_id: int) -> List[Dict]:
        """Получение новостей для модерации (админом)"""
        if not self._check_admin(admin_id):
            return []
        
        self.cursor.execute("SELECT * FROM news WHERE status = FALSE")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def approve_news(self, admin_id: int, news_id: int) -> bool:
        """Одобрение новости (админом)"""
        if not self._check_admin(admin_id):
            return False
        
        self.cursor.execute(
            "UPDATE news SET status = TRUE WHERE id = %s",
            (news_id,)
        )
        return self.cursor.rowcount > 0
    
    def reject_news(self, admin_id: int, news_id: int) -> bool:
        """Отклонение новости (админом)"""
        if not self._check_admin(admin_id):
            return False
        
        self.cursor.execute("DELETE FROM news WHERE id = %s AND status = FALSE", (news_id,))
        return self.cursor.rowcount > 0
    
    # Методы для работы с тегами
    def add_tag(self, name: str) -> Optional[int]:
        """Добавление нового тега"""
        try:
            self.cursor.execute(
                "INSERT INTO tags (name) VALUES (%s) RETURNING id",
                (name,)
            )
            return self.cursor.fetchone()['id']
        except psycopg2.IntegrityError:
            return None
    
    def get_all_tags(self) -> List[Dict]:
        """Получение списка всех тегов"""
        self.cursor.execute("SELECT * FROM tags")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def add_tag_to_news(self, user_id: int, news_id: int, tag_id: int) -> bool:
        """Добавление тега к новости"""
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
        """Добавление нового источника"""
        try:
            self.cursor.execute(
                "INSERT INTO sources (name, link) VALUES (%s, %s) RETURNING id",
                (name, link)
            )
            return self.cursor.fetchone()['id']
        except psycopg2.IntegrityError:
            return None
    
    def get_all_sources(self) -> List[Dict]:
        """Получение списка всех источников"""
        self.cursor.execute("SELECT * FROM sources")
        return [dict(row) for row in self.cursor.fetchall()]
    
    # Методы для работы с папками
    def create_folder(self, user_id: int, folder_name: str) -> Optional[int]:
        """Создание папки для пользователя"""
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
        """Добавление новости в папку"""
        # Проверяем, что папка принадлежит пользователю
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
        """Получение папок пользователя"""
        self.cursor.execute(
            """SELECT f.id, f.name, f.newsID 
               FROM folders f
               JOIN users u ON f.userLOG = u.user_login
               WHERE u.id = %s""",
            (user_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def suggest_news_source(self, user_id: int, link: str) -> bool:
        """Отправка предложения нового источника"""
        # Используем поле notification для хранения предложений
        self.cursor.execute(
            "UPDATE users SET notification = %s WHERE id = %s",
            (f"source_suggestion:{link}", user_id)
        )
        return self.cursor.rowcount > 0