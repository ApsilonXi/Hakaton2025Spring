import psycopg2

class News:
    def __init__(self, login, password, active_user):
        self.login = login
        self.password = password 

        if active_user:
            self.conn = active_user
        else:
            try:
                self.conn = psycopg2.connect(
                    host="127.0.0.1",
                    user=login,
                    password=password,
                    database="Warehouse_DB"
                )
                self.cursor = self.conn.cursor()
                print("[INFO] PostgreSQL connection open.")
            except Exception as ex:
                print(f"[ERROR] Connection failed: {ex}")
                return
            
    def on_close(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            print("[INFO] PostgreSQL connection closed.")

    def check_user_exist(self, login):
        '''Проверяет существование логина пользователя'''
        try:
            self.cursor.execute("""
                SELECT login 
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
            print(f'[LOAD ERROR] Failed to load data about users: {e}')        

    def insert_new_user(self, login, password, role):
        '''Добавление нового пользователя'''
        try:
            if self.check_user_exist(login):
                self.cursor.execute("""
                    INSERT INTO users (login, password, role)
                    VALUES (%s, %s, %s); 
                    """, (login, password, role))
                self.conn.commit()
        except Exception as e:
            print(f'[TRANSACTION] Failed insert user into database: {e}')
            
    def update_user_password(self, login, old_password, new_password):
        '''Обновление пароля пользователя'''
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
                raise ValueError('This user is not exist')
        except Exception as e:
            print(f'[TRANSACTION] Failed update user password: {e}')

    

    
            
    

            

