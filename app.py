from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, send_file, make_response
from scripts_bd.db_methods import *
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
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
    
    # Получаем все опубликованные новости из базы данных
    news = DB.get_published_news()
    
    # Фильтруем только актуальные новости (type_news == False)
    actual_news = [item for item in news if not item['type_news']]
    
    return render_template("index.html", 
                         user_info=user_info, 
                         news=news,
                         actual_news=actual_news[:5])  # Ограничиваем до 5 новостей

@app.route("/news/<int:news_id>")
def news_page(news_id):
    # Получаем новость из базы данных
    news_item = DB.get_news_by_id(news_id)
    
    if not news_item:
        flash('Новость не найдена', 'error')
        return redirect(url_for('index'))
    
    # Получаем актуальные новости для боковой панели
    all_news = DB.get_published_news()
    actual_news = [item for item in all_news if not item['type_news']]
    
    return render_template("news_page.html", 
                         news_item=news_item,
                         actual_news=actual_news[:5])



def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

@app.route('/download-pdf')
def download_pdf():
    try:
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        pdfmetrics.registerFont(TTFont('DejaVu', 'static/DejaVuSans.ttf'))
        p.setFont("DejaVu", 12)

        title = request.args.get('title', 'Название статьи')
        date = request.args.get('date', '01.01.2025')
        tags = request.args.get('tags', 'Без тега')
        content = request.args.get('content', 'Содержание статьи')

        # Очистим заголовок, чтобы использовать как имя файла
        safe_title = sanitize_filename(title) + ".pdf"

        y = 800
        p.setFont("DejaVu", 16)
        p.drawString(50, y, title)
        y -= 30

        p.setFont("DejaVu", 12)
        p.drawString(50, y, f"Дата: {date}")
        y -= 20
        p.drawString(50, y, f"Теги: {tags}")
        y -= 30

        text = p.beginText(50, y)
        text.setFont("DejaVu", 12)
        for line in content.split('\n'):
            text.textLine(line)
        p.drawText(text)

        p.showPage()
        p.save()

        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=safe_title,
            mimetype='application/pdf'
        )
    except Exception as e:
        return str(e), 500


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

@app.route("/my_profile", methods=['GET', 'POST'])
def my_profile():
    # Проверка авторизации и что пользователь не админ
    if 'user' not in session:
        flash('Для доступа к этой странице необходимо авторизоваться', 'error')
        return redirect(url_for('login'))
    
    if session['user']['role'] == 'admin':
        flash('Администраторы не имеют доступа к этой странице', 'error')
        return redirect(url_for('index'))
    
    user_id = session['user']['id']
    message = None
    
    # Обработка смены пароля
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        
        if not old_password or not new_password:
            flash('Все поля должны быть заполнены', 'error')
        else:
            success = DB.change_password(user_id, old_password, new_password)
            if success:
                flash('Пароль успешно изменен', 'success')
            else:
                flash('Неверный старый пароль', 'error')
    
    # Генерация токена (id + user_login)
    token = f"{session['user']['id']}{session['user']['login']}"
    
    return render_template("my_profile.html", 
                         user_info=session['user'],
                         token=token)

@app.route("/suggest_news", methods=['GET', 'POST'])
def suggest_news():
    # Проверка авторизации и что пользователь не админ
    if 'user' not in session:
        flash('Для доступа к этой странице необходимо авторизоваться', 'error')
        return redirect(url_for('login'))
    
    if session['user']['role'] == 'admin':
        flash('Администраторы не имеют доступа к этой странице', 'error')
        return redirect(url_for('index'))
    
    user_id = session['user']['id']
    
    if request.method == 'POST':
        link = request.form.get('link')
        
        if not link:
            flash('Поле ссылки не может быть пустым', 'error')
        else:
            success = DB.suggest_news_source(user_id, link)
            if success:
                flash('Ссылка успешно отправлена на рассмотрение', 'success')
                return redirect(url_for('index'))
            else:
                flash('Произошла ошибка при отправке предложения', 'error')
    
    return render_template("suggest_news.html", 
                         user_info=session['user'])


@app.route("/create_news", methods=['GET', 'POST'])
def create_news():
    # Проверка авторизации и что пользователь админ или верифицированный
    if 'user' not in session:
        flash('Для доступа к этой странице необходимо авторизоваться', 'error')
        return redirect(url_for('login'))
    
    if session['user']['role'] not in ('admin', 'verified'):
        flash('Только админы и верифицированные пользователи могут создавать новости', 'error')
        return redirect(url_for('index'))
    
    user_id = session['user']['id']
    
    # Получаем список доступных тегов из базы данных
    tags = DB.get_all_tags()
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        source_link = request.form.get('source_link')
        source_name = request.form.get('source_name')
        tag_id = request.form.get('tag_id')
        is_organization = request.form.get('is_organization') == 'on'
        
        if not title or not content:
            flash('Заголовок и содержание новости обязательны для заполнения', 'error')
        else:
            # Получаем или создаем источник по ссылке
            source_id = None
            
            if source_link:
                source_id = DB.get_or_create_source(source_link)
            
            # Преобразуем tag_id в int, если он есть
            tag_id = int(tag_id) if tag_id else None
            
            news_id = DB.add_news(
                user_id=user_id,
                title=title,
                content=content,
                tag_id=tag_id,
                source_id=source_id,
                is_organization=is_organization
            )
            
            if news_id:
                flash('Новость успешно добавлена!', 'success')
                return redirect(url_for('news_page', news_id=news_id))
            else:
                flash('Произошла ошибка при добавлении новости', 'error')
    
    return render_template("create_news.html", 
                         user_info=session['user'],
                         tags=tags)

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