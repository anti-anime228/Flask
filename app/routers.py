import secrets
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from app import db
from .models import Users, Secrets
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from .forms import LoginForm
from .auth import load_user
import sqlite3
from random import choice


bp = Blueprint('main', __name__, template_folder='templates')
secret_key = secrets.token_hex(16)



def init_app(app):
    app.register_blueprint(bp)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    print('1')
    form = LoginForm()
    print('2')
    if form.validate_on_submit():
        print('3')
        username = form.username.data
        password = form.password.data
        print('4')
        user = Users.query.filter_by(username=username).first()
        print('5')
        if user is not None and user.check_password(password):
            print('6')
            login_user(user)
            print('7')
            next_page = request.args.get('next')
            print('8')
            return redirect(
                next_page or url_for('main.protected'))  # Укажите маршрут для перенаправления после успешного входа
        else:
            flash('Неверное имя пользователя или пароль.', 'error')
    return render_template('login.html', form=form)


@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы.')
    return redirect(url_for('main.home'))




@bp.route('/protected')
@login_required
def protected():
    conn = sqlite3.connect('instance/db.db')
    cur = conn.cursor()
    cur.execute("SELECT content FROM secrets")
    rows = cur.fetchall()

    random_secret = choice(rows)[0]
    conn.close()
    return render_template('protected.html', secret=random_secret)


@bp.route('/get-random-secret')
@login_required
def get_random_secret():
    conn = sqlite3.connect('instance/db.db')
    cur = conn.cursor()
    cur.execute("SELECT content FROM secrets")
    rows = cur.fetchall()
    random_secret = choice(rows)[0]
    conn.close()
    return jsonify({'secret': random_secret})


@bp.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
        age = request.form.get('age')
        if not all([username, email, password, repeat_password, age]):
            flash("Пожалуйста, заполните все поля.")
            return render_template('registration.html')
        elif password != repeat_password:
            flash("Пароли не совпадают")
            return render_template('registration.html')
        elif int(age) < 18:
            flash("Вы должны быть старше 18 лет!")
            return render_template('registration.html')
        try:
            conn = sqlite3.connect('instance/db.db', check_same_thread=False)
            cursor = conn.cursor()

            cursor.execute("SELECT username FROM Users WHERE username = ?", (username,))
            existing_username = cursor.fetchone()
            if existing_username:
                conn.close()
                flash("Такой пользователь уже существует")
                return render_template('registration.html')

            cursor.execute("SELECT email FROM Users WHERE email = ?", (email,))
            existing_email = cursor.fetchone()
            if existing_email:
                conn.close()
                flash("Такая почта уже зарегистрирована")
                return render_template('registration.html')

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            cursor.execute('INSERT INTO users (username, email, password, age) VALUES (?, ?, ?, ?)',
                           (username, email, hashed_password, age))
            conn.commit()
            conn.close()
            flash("Пользователь успешно зарегистрирован!")
            return render_template('registration.html')

        except Exception as e:
            print(f"Ошибка при работе с базой данных: {e}")
            flash("Произошла ошибка при регистрации. Попробуйте позже.")
            return render_template('registration.html')


@bp.route('/secret', methods=['GET', 'POST'])
def secret():
    if request.method == 'GET':
        return render_template('secret.html')
    elif request.method == 'POST':
        try:
            content = request.form.get('content')
            created_at = datetime.now()

            conn = sqlite3.connect('instance/db.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO secrets (content, created_at) VALUES (?, ?)", (content, created_at))
            conn.commit()
            flash("Секрет сохранен")
            return render_template('secret.html')

        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                flash('Такой секрет уже существует.')
                return render_template('secret.html')
        except Exception as e:
            print(f"Ошибка при работе с базой данных: {e}")
            flash("Произошла ошибка при регистрации. Попробуйте позже.")
            return render_template('secret.html')
        finally:
            conn.close()

    return render_template('template.html')


if __name__ == '__main__':
    app.run(debug=True)
