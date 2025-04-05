from scripts_bd.db_methods import *
from flask import Flask, render_template, redirect, url_for, request, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Необходимо для работы flash-сообщений
DB = NewsDB(password="password")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Проверка на пустые поля
        if not username or not password:
            flash('Логин и пароль обязательны для заполнения', 'error')
            return redirect(url_for('register'))
        
        # Регистрация пользователя
        user_id = DB.register_user(username, password)
        
        if user_id:
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Пользователь с таким логином уже существует', 'error')
            return redirect(url_for('register'))
    
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)