from flask import Flask, render_template, redirect, url_for, request, flash, session
from scripts_bd.db_methods import *

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Важно использовать надежный ключ в продакшене
DB = NewsDB(password="password")

@app.route("/")
def index():
    return render_template("index.html")

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
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'error')
            return redirect(url_for('login'))
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user', None)
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)