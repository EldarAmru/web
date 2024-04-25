from flask import Flask, render_template, redirect, url_for, make_response, jsonify
from data import db_session, api
from data.users import User
from data.books import Book
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, EmailField, BooleanField, DateTimeField
from wtforms.validators import DataRequired
import hashlib
from flask_login import LoginManager, login_user, logout_user, current_user

db_session.global_init('db/database.db')
session = db_session.create_session()

login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(int(user_id))


app.config['SECRET_KEY'] = 'aoh;jlknsdg;oihkl'


class RegiterForm(FlaskForm):
    username = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторить пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    genres = StringField('Любимые жанры книг', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class LoginForm(FlaskForm):
    email = EmailField('Логин / Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class BookForm(FlaskForm):
    book = StringField('Название книги', validators=[DataRequired()])
    genre1 = StringField('Жанр', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    description = StringField(
        'Описание книги', validators=[DataRequired()])
    mark = StringField(
        'Оценка по 10 бальной шкале', validators=[DataRequired()])
    is_finished = BooleanField(
        'Уже прочитана')
    submit = SubmitField('Добавить книгу')


def custom_render(name: str, **params):
    params['style_url'] = url_for('static', filename='css/main.css')
    return render_template(name, **params)


@app.route('/')
@app.route('/index')
def index():
    session = db_session.create_session()
    n = session.query(Book).all()
    return custom_render('index.html', books1=n)


@app.route('/success')
def success():
    return custom_render('success.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegiterForm()
    if form.validate_on_submit():
        user = User()
        user.email = form.username.data
        user.hashed_password = hashlib.sha256(
            form.password.data.encode('utf-8')).hexdigest()
        user.surname = form.surname.data
        user.name = form.name.data
        user.genres = form.genres.data

        session.add(user)
        session.commit()

        login_user(user)

        return redirect('/')
    params = {'form': form}
    return custom_render('register.html', **params)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        params = {'message': 'Неправельный логин или пароль', 'form': form}
        return custom_render('login.html', **params)
    return custom_render('login.html', form=form)


@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        book = Book()
        book.book = form.book.data
        book.genre1 = form.genre1.data
        book.author = form.author.data
        book.description = form.description.data
        book.mark = form.mark.data
        book.is_finished = bool(form.is_finished.data)
        session.add(book)
        session.commit()
        return redirect('/')

    params = {'form': form}
    return custom_render('add_book.html', **params)



@app.route('/book-added-successfully')
def book_added_successfully():
    return custom_render('added_successfully.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.errorhandler(400)
def bad_request():
    return make_response(jsonify({'error': 'Bad request'}), 400)


if __name__ == '__main__':
    app.register_blueprint(api.blueprint)
    app.run(port=8081, host='127.0.0.1')
