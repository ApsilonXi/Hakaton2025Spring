import psycopg2
import time

class News:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password 

        try:
            self.conn = psycopg2.connect(
                host="127.0.0.1",
                user=login,
                password=password,
                database="news_bd"
            )
            self.cursor = self.conn.cursor()
            print("[INFO] PostgreSQL connection open.")
        except Exception as ex:
            print(f"[ERROR] Connection failed: {ex}")
            
    def on_close(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            print("[INFO] PostgreSQL connection closed.")

    def check_user_exist(self, login: str):
        '''Проверка существования логина пользователя'''
        try:
            self.cursor.execute("""
                SELECT * 
                  FROM users
                 WHERE login = %s
                 LIMIT 1;
                """, (login,))
            user = self.cursor.fetchall()
            if user != []:
                return True
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            print(f'[LOAD ERROR] Failed to load data about users: {e}')   

    def check_folder_exist(self, folder_name: str):
        '''Проверка существования папки пользователя'''
        try:
            self.cursor.execute("""
                SELECT *
                  FROM folders
                 WHERE folder_name = %s
                 LIMIT 1;
                """, (folder_name,))
            folder = self.cursor.fetchall()
            if folder != []:
                return True
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            print(f'[LOAD ERROR] Failed to load data about folder: {e}')   

    def check_news_exist(self, news_title: str, news_content: str):
        '''Проверка существования публикации на сайте'''
        try:
            self.cursor.execute("""
                SELECT *
                  FROM news
                 WHERE news_title = %s
                   AND news_content = %s
                   AND type_news = True
                 LIMIT 1;
                """, (news_title, news_content))
            news = self.cursor.fetchall()
            if news != []:
                return True
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            print(f'[LOAD ERROR] Failed to load data about news: {e}') 

    def check_source_exist(self, source_name: str):
        '''Проверка существования информационного ресурса'''
        try:
            self.cursor.execute("""
                SELECT *
                  FROM sources
                 WHERE source_name = %s
                 LIMIT 1;
                """, (source_name,))
            sources = self.cursor.fetchall()
            if sources != []:
                return True
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            print(f'[LOAD ERROR] Failed to load data about source: {e}') 
    
    def check_tag_exist(self, tag_name):
        '''Проверка существования тега в системе'''
        try:
            self.cursor.execute("""
                SELECT *
                  FROM tags
                 WHERE tag_name = %s
                 LIMIT 1;
                """, (tag_name,))
            tags = self.cursor.fetchall()
            if tags != []:
                return True
            else:
                return False
        except Exception as e:
            self.conn.rollback()
            print(f'[LOAD ERROR] Failed to load data about tags: {e}') 

    def load_folders(self, login: str):
        '''Получение папок пользователя'''
        try:
            if self.check_user_exist(login):
                self.cursor.execute("""
                    SELECT folder_name
                      FROM folders
                     WHERE userLOG = %s;
                    """, (login,))
                folders = self.cursor.fetchall()
                if folders != []:
                    return folders
                else:
                    self.conn.rollback()
                    raise ValueError("This user doesn't have folders")
            else:
                self.conn.rollback()
                raise ValueError(f'[LOAD ERROR] Failed to load data about user: {e}')
        except Exception as e:
                self.conn.rollback()
                print(f"[LOAD ERROR] Failed to load data about user's folders: {e}")

    def load_news_from_folders(self, login: str):
        '''Получение статей, сохраненых в папке пользователя'''
        try:
            folder_news = {}
            if self.check_user_exist(self):
                folders = self.load_folders(login)
                for name in folders:
                    self.cursor.execute("""
                        SELECT s.source_name, n.news_title, n.news_content
                          FROM folders f
                          JOIN news n 
                            ON f.newsID = n.news_id
                          JOIN source
                            ON n.sourceID = s.source_id
                         WHERE f.folder_name = %s
                           AND f.userLOG = %s;
                        """, (name, login))
                    folder_news[name] = list(self.cursor.fetchall())
                    return folder_news
            else:
                self.conn.rollback()
                raise ValueError(f'[LOAD ERROR] Failed to load data about user: {e}')
        except Exception as e:
            self.conn.rollback()
            print(f'[LOAD ERROR] Failed load news from folder: {e}')

    def insert_new_user(self, login: str, password: str, role: str = 'user'):
        '''Добавление нового пользователя'''
        try:
            if self.check_user_exist(login):
                self.cursor.execute("""
                    INSERT INTO users (login, password, role)
                    VALUES (%s, %s, %s); 
                    """, (login, password, role))
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f'[TRANSACTION] Failed insert user into database: {e}')
            
    def update_user_password(self, login: str, old_password: str, new_password: str):
        '''Обновление пароля пользователя'''
        # пользователь ОБЯЗАН указать свой старый пароль, чтобы обновить его
        try:
            self.cursor.execute("""
                SELECT login, password
                  FROM users
                 WHERE login = %s 
                   AND password = %s;
                """, (login, old_password))
            user = self.cursor.fetchall()
            if user != []:
                self.cursor.execute("""
                    UPDATE users
                       SET password = %s
                     WHERE login = %s
                       AND password = %s;
                    """, (new_password, login, new_password))
                self.conn.commit()
            else:
                self.conn.rollback()
                raise ValueError('This user is not exist')
        except Exception as e:
            self.conn.rollback()
            print(f'[TRANSACTION] Failed update user password: {e}')

    def create_folder_user(self, login: str, folder_name: str):
        '''Создание пустой папки (подборки)'''
        try:
            if self.check_user_exist(login):
                if self.check_folder_exist(folder_name):
                    self.cursor.execute("""
                        INSERT INTO folders (userLOG, folder_name)
                        VALUES (%s, %s);
                        """, (login, folder_name))
                    self.conn.commit()
                else:
                    self.conn.rollback()
                    raise ValueError('This folder alredy exist')
            else:
                self.conn.rollback()
                raise ValueError(f'[LOAD ERROR] Failed load data about user: {e}')
        except Exception as e:
            self.conn.rollback()
            print(f'[TRANSACTION] Failed create folder: {e}')

    def add_news_to_folder(self, login: str, folder_name: str, title: str, content: str):
        '''Добавление публикации в папку пользователя'''
        try:
            if self.check_user_exist(login):
                if self.check_folder_exist(folder_name):
                    self.cursor.execute("""
                        INSERT INTO folders (userLOG, folder_name, newsID)
                        VALUES (%s, %s, %s);
                        """, (login, folder_name, self.get_news_id(title, content)))
                    self.conn.commit()
                else:
                    self.conn.rollback()
                    raise ValueError('This folder alredy exist')
            else:
                self.conn.rollback()
                raise ValueError(f'[LOAD ERROR] Failed load data about folder: {e}')
        except Exception as e:
            self.conn.rollback()
            print(f'[TRANSACTION] Failed add news to folder: {e}')

    def delete_news_from_folder(self, login: str, folder_name: str, news_title: str, news_content: str):
        '''Удаление публикации из папки пользователя'''
        try:
            if self.check_folder_exist(folder_name):
                if self.check_news_exist(news_title, news_content):
                    self.cursor.execute("""
                        SELECT news_id
                         WHERE news_title = %s
                           AND news_content %s;
                        """)
                    news = self.cursor.fetchall()
                    self.cursor.execute("""
                        DELETE FROM folders
                         WHERE newsID = %s
                           AND userLOG = %s;
                        """, (news, login))
                    self.conn.commit()
                else:
                    self.conn.rollback()
                    raise ValueError('This folder alredy exist')
            else:
                self.conn.rollback()
                raise ValueError(f'[LOAD ERROR] Failed load data about folder: {e}')
        except Exception as e:
            self.conn.rollback()
            print(f'[TRANSACTION] Failed delete news from folder: {e}')



    def add_new_news(self, type_news: bool, news_title: str, news_content: str, date: time, status: bool, tags: list, source: str):
        '''Добавление новой публикации на сайт'''
        try:
            if self.check_news_exist(news_title, news_content):
                raise ValueError('This news is alredy exist')
            else:
                for tag in tags:
                    self.cursor.execute("""
                        SELECT tag_id 
                          FROM tags
                         WHERE tag_name = %s;
                        """, (tag,))
                    tag_id = self.cursor.fetchall()
                    self.cursor.execute("""
                        SELECT source_id 
                          FROM source
                         WHERE source_name = %s;
                        """, (source,))
                    source_id = self.cursor.fetchall()
                    self.cursor.execute("""
                        INSERT INTO news (type_news, news_title, news_content, date, status, tagID, sourceID)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """, (type_news, news_title, news_content, date, status, tag_id, source_id))
                    self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f'[TRANSACTION] Failed delete news from folder: {e}')

    def update_news(self, type_news: bool=None, news_title: str=None, news_content: str=None, date: time=None, status: bool=None, tags: list=None, source: str=None):
        '''Редактирование новости на сайте'''
        try:
            if self.check_news_exist(news_title, news_content):
                sql = "SET "
                self.cursor.execute("""
                    UPDATE news
                       SET 
                    """)
        except Exception as e:
            self.conn.rollback()
            print(f'[TRANSACTION] Failed update news in database: {e}')





    

    
            
    

            

