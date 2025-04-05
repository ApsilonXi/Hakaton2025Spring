from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    # Здесь можно добавить логику для страницы регистрации
    return render_template("register.html")  # Создайте этот шаблон позже

@app.route("/login")
def login():
    # Здесь можно добавить логику для страницы входа
    return render_template("login.html")  # Создайте этот шаблон позже

if __name__ == "__main__":
    app.run(debug=True)
    