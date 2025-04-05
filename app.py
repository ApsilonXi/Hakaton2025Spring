from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from scripts_bd.db_methods import *

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Важно использовать надежный ключ в продакшене
DB = NewsDB(password="password")

@app.route("/")
def index():
    user_info = None
    if 'user' in session:
        user_info = {
            'login': session['user']['login'],
            'role': session['user']['role']
        }
    
    # Получаем опубликованные новости из базы данных
    news = DB.get_published_news()
    
    return render_template("index.html", user_info=user_info, news=news)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Логин и пароль обязательны для заполнения', 'error')
            return redirect(url_for('register'))
        
        user_id = DB.register_user(username, password)
        
        if user_id:
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Пользователь с таким логином уже существует', 'error')
            return redirect(url_for('register'))
    
    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    # Если пользователь уже авторизован, перенаправляем на главную
    if 'user' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Логин и пароль обязательны для заполнения', 'error')
            return redirect(url_for('login'))
        
        print((DB.authenticate_user(username, password)))
        user = DB.authenticate_user(username, password)
        
        if user:
            # Сохраняем пользователя в сессии
            session['user'] = {
                'id': user['id'],
                'login': user['login'],
                'role': user['role']
            }
            print("Session user:", session['user'])
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'error')
            return redirect(url_for('login'))
    
    return render_template("login.html")

@app.route("/my_folders")
def my_folders():
    if 'user' not in session:
        flash('Для доступа к этой странице необходимо авторизоваться', 'error')
        return redirect(url_for('login'))
    
    # Получаем папки текущего пользователя
    folders = DB.get_user_folders(session['user']['id'])
    return render_template("my_folders.html", folders=folders)

@app.route("/create_folder", methods=['POST'])
def create_folder():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Требуется авторизация'}), 401
    
    data = request.get_json()
    folder_name = data.get('folder_name')
    
    if not folder_name:
        return jsonify({'success': False, 'message': 'Название папки не может быть пустым'}), 400
    
    folder_id = DB.create_folder(session['user']['id'], folder_name)
    if folder_id:
        return jsonify({'success': True, 'folder_id': folder_id})
    else:
        return jsonify({'success': False, 'message': 'Не удалось создать папку'}), 400

@app.route("/delete_folder", methods=['POST'])
def delete_folder():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Требуется авторизация'}), 401
    
    data = request.get_json()
    folder_id = data.get('folder_id')
    
    if not folder_id:
        return jsonify({'success': False, 'message': 'Не указана папка для удаления'}), 400
    
    # Проверяем, что папка принадлежит пользователю
    folders = DB.get_user_folders(session['user']['id'])
    if not any(folder['id'] == folder_id for folder in folders):
        return jsonify({'success': False, 'message': 'Папка не найдена или нет прав доступа'}), 403
    
    # Удаляем папку (нужно реализовать метод в DB)
    success = DB.delete_folder(folder_id)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Не удалось удалить папку'}), 500

@app.route("/folder/<int:folder_id>")
def folder_content(folder_id):
    if 'user' not in session:
        flash('Для доступа к этой странице необходимо авторизоваться', 'error')
        return redirect(url_for('login'))
    
    # Проверяем, что папка принадлежит пользователю
    folders = DB.get_user_folders(session['user']['id'])
    if not any(folder['id'] == folder_id for folder in folders):
        flash('Папка не найдена или нет прав доступа', 'error')
        return redirect(url_for('my_folders'))
    
    # Получаем новости из папки (нужно реализовать метод в DB)
    news = DB.get_news_in_folder(folder_id)
    return render_template("folder_content.html", news=news, folder_name=next(f['name'] for f in folders if f['id'] == folder_id))


@app.route("/logout")
def logout():
    session.pop('user', None)
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)