from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


# Этот класс будет представлять администратора сайта
class Admin(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.username = username
        self.password = password

    # Метод проверки пароля
    def check_password(self, password):
        return self.password == password


# Функция, которая будет вызываться для проверки учетных данных пользователя
@login_manager.user_loader
def load_user(user_id):
    # Вместо простого словаря можно использовать базу данных или другой механизм хранения пользователей
    users = {'admin': Admin('admin', 'admin')}
    return users.get(user_id)


# Основная страница панели управления
@app.route('/admin/')
@login_required
def admin_panel():
    return render_template('layout.html')


# Страница входа для администратора
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_panel'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = load_user(username)

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_panel'))

    return render_template('admin_login.html')


# Страница выхода из панели управления
@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))


