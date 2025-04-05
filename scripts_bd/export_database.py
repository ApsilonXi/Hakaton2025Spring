from db_config import *

'''ручной ввод: "C:\Program Files\PostgreSQL\17\bin\pg_dump" -U postgres -h localhost -p 5432 -d news_bd -F c -f "D:\GitGub\Hakaton2025Spring\backup\backup.sql"'''
# фукнция чтобы полностью выгружать базу данных, со всеми триггерами, процедурами, таблицами, данными из таблицы в sql файл
def create_backup(password:str):
    """
    : password: пароль подключения к бд, такой же как указано в db_config.py
    """

    # Получаем параметры подключения из функции get_db_connection (файл db_config.py)
    conn = get_db_connection('news_db', 'postgres', '12345', 'localhost', '5432')
    db_params = conn.get_dsn_parameters()
    conn.close()

    # Устанавливаем переменную окружения PGPASSWORD
    os.environ['PGPASSWORD'] = password


    # Путь к утилите pg_dump
    pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
    
    # Параметры для резервного копирования
    username = db_params['user']
    host = db_params['host']
    port = db_params['port']
    database = db_params['dbname']
    backup_file = os.path.join(f"backup/backup.sql")

    # Команда для выполнения резервного копирования
    command = [
        pg_dump_path, 
        "-U", username, 
        "-h", host, 
        "-p", port, 
        "-F", "p", 
        "-f", backup_file, 
        database
    ]

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("Успех", "Резервное копирование успешно завершено!")
    except subprocess.CalledProcessError as e:
        print("Ошибка", f"Ошибка при создании бекапа: {e}")

<<<<<<< HEAD
"""
    ПРИМЕР ВЫЗОВА:
    create_backup("password")
"""
create_backup('12345')
=======
'''create_backup("12345")  - мила'''
>>>>>>> emiliya
