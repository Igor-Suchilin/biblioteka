from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from sweater import app, db
from sweater.models import Article, User

# главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница добавления книги
@app.route('/add-book', methods=['POST', 'GET'])
@login_required
def add_book():
    if request.method == 'POST': # если метод POST
        title = request.form['title']
        writer = request.form['writer']
        text = request.form['text']

        book = Article(title=title, writer=writer, text=text) # создаем объект book

        try:
            db.session.add(book) # добавляем объект book в базу данных
            db.session.commit() # закрываем сессию добавления
            return redirect('/') # перенос на главную страницу
        except:
            return 'При добавлении книги произошла ошибка'
    else:
        return render_template('add-book.html')

# Страница со списком книг
@app.route('/all-books')
def all_books():
    q = request.args.get('q') # Реализация поиска. Есди был запрос то показывать согласно запросу
    if q:
        books = Article.query.filter(Article.title.contains(q) | Article.writer.contains(q)).all()
    else:
        books = Article.query.order_by(Article.date.desc()).all() # Если нет то все книги
    return render_template('all-books.html', books=books)

# Просмотр отдельной книги
@app.route('/all-books/<int:id>')
def book_detail(id):
    book = Article.query.get(id)
    return render_template('book-detail.html', book=book)

# Метод удаления книги
@app.route('/all-books/<int:id>/delete')
@login_required # Ограницение доступа
def book_delete(id):
    book = Article.query.get_or_404(id)
    try:
        db.session.delete(book)
        db.session.commit()
        return redirect('/all-books')
    except:
        return 'При удалении статьи произошла ошибка'

# Метод редактирования информации о книге
@app.route('/all-books/<int:id>/update', methods=['POST', 'GET'])
@login_required # Ограницение доступа
def book_update(id):
    article = Article.query.get(id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.writer = request.form['writer']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/all-books')
        except:
            return 'При обновлении книги произошла ошибка'
    else:
        book = Article.query.get(id)
        return render_template('book-update.html', book=book)


# Метод входа в режим администратора
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')

            return redirect(next_page)
        else:
            flash('Login or password is not correct')
    else:
        flash('Please fill login and password fields')

    return render_template('login.html')


# Метод регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))

    return render_template('register.html')

# Метод выхода
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

# Метод перенаправления на страницу аторизации при отказе в доступе к закрытой странице
@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response
