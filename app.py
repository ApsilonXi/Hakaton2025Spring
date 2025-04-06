from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, send_file, make_response
from db_methods import *
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime
import re

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Важно использовать надежный ключ в продакшене
DB = NewsDB(password="12345")

@app.route("/")
def index():
    user_info = None
    if 'user' in session:
        user_info = {
            'login': session['user']['login'],
            'role': session['user']['role']
        }
    
    # Получаем новости и форматируем даты
    news = DB.get_published_news()
    for item in news:
        if 'date' in item and item['date']:  # Проверяем наличие даты
            if isinstance(item['date'], str):  # Если дата - строка
                # Преобразуем строку в datetime объект (используем strptime, а не stryttae)
                try:
                    item['date'] = datetime.datetime.strptime(item['date'], '%Y-%m-%d')
                except ValueError:
                    # Если формат даты не совпадает, используем текущую дату
                    item['date'] = datetime.datetime.now()
            # Если это уже datetime объект, оставляем как есть
        else:
            item['date'] = datetime.datetime.now()  # Или установите дату по умолчанию
    
    actual_news = [item for item in news if not item.get('type_news', False)]
    
    return render_template("index.html",
                         user_info=user_info, 
                         news=news,
                         actual_news=actual_news[:5])

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

@app.route('/api/offers')
def get_offers():
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({"error": "Требуются права администратора"}), 403
    
    try:
        offers = DB.get_offers_for_moderation()
        return jsonify(offers)
    except Exception as e:
        print(f"Ошибка в /api/offers: {str(e)}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

@app.route('/api/offers/<int:offer_id>/<action>', methods=['POST'])
def process_offer(offer_id, action):
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({"error": "Требуются права администратора"}), 403
        
    if action not in ('approve', 'reject'):
        return jsonify({"error": "Недопустимое действие"}), 400
    
    try:
        success = DB.process_offer(offer_id, action)
        if success:
            return jsonify({"success": True})
        return jsonify({"error": "Не удалось обработать предложение"}), 400
    except Exception as e:
        print(f"Ошибка обработки предложения: {str(e)}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500
    
@app.route("/my_subscriptions")
def my_subscriptions():
    if 'user' not in session:
        flash('Для доступа к этой странице необходимо авторизоваться', 'error')
        return redirect(url_for('login'))
    
    # Получаем подписки пользователя
    user_id = session['user']['id']
    tag_subscriptions = DB.get_user_tag_subscriptions(user_id)
    source_subscriptions = DB.get_user_source_subscriptions(user_id)
    
    # Получаем популярные теги и источники для модального окна
    popular_tags = DB.get_popular_tags()
    popular_sources = DB.get_popular_sources()
    
    return render_template("my_subscriptions.html",
                         user_info=session['user'],
                         tag_subscriptions=tag_subscriptions,
                         source_subscriptions=source_subscriptions,
                         popular_tags=popular_tags,
                         popular_sources=popular_sources)
    
@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Требуется авторизация'}), 401
    
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Неверный формат данных'}), 415
    
    try:
        data = request.get_json()
        sub_type = data.get('type')
        sub_id = data.get('id')
        
        if not sub_type or not sub_id:
            return jsonify({'success': False, 'message': 'Не указаны параметры подписки'}), 400
        
        if sub_type == 'tag':
            success = DB.subscribe_to_tag(session['user']['id'], sub_id)
        elif sub_type == 'source':
            success = DB.subscribe_to_source(session['user']['id'], sub_id)
        else:
            return jsonify({'success': False, 'message': 'Неверный тип подписки'}), 400
        
        return jsonify({'success': success, 'message': 'Подписка успешно добавлена'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/unsubscribe', methods=['POST'])
def unsubscribe():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Требуется авторизация'}), 401
    
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Неверный формат данных'}), 415
    
    try:
        data = request.get_json()
        sub_type = data.get('type')
        sub_id = data.get('id')
        
        if not sub_type or not sub_id:
            return jsonify({'success': False, 'message': 'Не указаны параметры подписки'}), 400
        
        if sub_type == 'tag':
            success = DB.unsubscribe_from_tag(session['user']['id'], sub_id)
        elif sub_type == 'source':
            success = DB.unsubscribe_from_source(session['user']['id'], sub_id)
        else:
            return jsonify({'success': False, 'message': 'Неверный тип подписки'}), 400
        
        return jsonify({'success': success, 'message': 'Отписка выполнена успешно'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
@app.route('/my_folders_data')
def my_folders_data():
    if 'user' not in session:
        return jsonify({'error': 'Требуется авторизация'}), 401
    
    folders = DB.get_user_folders(session['user']['id'])
    # Добавляем количество новостей в каждой папке
    folders_with_count = []
    for folder in folders:
        news_count = DB.get_news_count_in_folder(folder['id'])
        folders_with_count.append({
            'id': folder['id'],
            'name': folder['name'],
            'news_count': news_count
        })
    
    return jsonify(folders_with_count)

@app.route("/add_to_folder", methods=['POST'])
def add_to_folder():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Требуется авторизация'}), 401
    
    data = request.get_json()
    news_id = data.get('news_id')
    folder_id = data.get('folder_id')
    
    if not news_id or not folder_id:
        return jsonify({'success': False, 'message': 'Не указаны новость или папка'}), 400
    
    # Проверяем, что папка принадлежит пользователю
    folders = DB.get_user_folders(session['user']['id'])
    if not any(folder['id'] == folder_id for folder in folders):
        return jsonify({'success': False, 'message': 'Папка не найдена или нет прав доступа'}), 403
    
    # Проверяем, есть ли уже новость в папке
    if DB.is_news_in_folder(news_id, folder_id):
        return jsonify({'success': False, 'message': 'Эта новость уже есть в выбранной папке'}), 400
    
    # Добавляем новость в папку
    success = DB.add_news_to_folder(session['user']['id'], folder_id, news_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Новость успешно сохранена'})
    else:
        return jsonify({'success': False, 'message': 'Не удалось сохранить новость'}), 500
    
@app.route("/admin")
def admin_panel():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    users = DB.all_users()
    print(f"DEBUG: Found {len(users)} users")  # Отладочный вывод
    return render_template("admin_panel.html", 
                         users=users,
                         user_info=session['user'])

@app.route('/api/change_user_role', methods=['POST'])
def change_user_role():
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Требуются права администратора'}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    new_role = data.get('new_role')
    
    try:
        DB.cursor.execute(
            "UPDATE users SET user_role = %s WHERE id = %s",
            (new_role, user_id)
        )
        DB.conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        DB.conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/following')
def following():
    if 'user' not in session:
        flash('Для доступа к этой странице необходимо авторизоваться', 'error')
        return redirect(url_for('login'))
    
    # Получаем новости по подпискам пользователя
    user_id = session['user']['id']
    subscribed_news = DB.get_news_by_user_subscriptions(user_id)
    
    # Получаем актуальные новости для боковой панели
    all_news = DB.get_published_news()
    actual_news = [item for item in all_news if not item['type_news']]
    
    # Получаем популярные теги
    popular_tags = [tag['name'] for tag in DB.get_popular_tags()]
    
    return render_template("index.html", 
                         news=subscribed_news,
                         actual_news=actual_news[:5],
                         popular_tags=popular_tags,
                         is_following_view=True)

if __name__ == "__main__":
    app.run(debug=True)