from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, timedelta
=======
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'supersecretkey'  # Cambia esto por una clave secreta más segura
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile = db.Column(db.String(50), nullable=False)
    loans = db.relationship('Loan', backref='loan_user', lazy=True)  # Renombrar el backref

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    nationality = db.Column(db.String(250), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    book_count = db.Column(db.Integer, default=0)
    books = db.relationship('Book', backref='author', lazy=True)

=======
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'  # Clave secreta para proteger las sesiones y cookies
db = SQLAlchemy(app)

# Define el modelo de Libro

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    rating = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'), nullable=False)
    publisher = db.relationship('Publisher', backref='published_books')

class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    books = db.relationship('Book', backref='genre', lazy=True)
    authors = db.relationship('Author', backref='genre', lazy=True)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    book = db.relationship('Book', backref='loans')
    user = db.relationship('User', backref='user_loans')  # Renombrar el backref para evitar conflicto

class BookReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    book = db.relationship('Book', backref='reviews')
    user = db.relationship('User', backref='reviews')

# Define el modelo de Usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    # Método para establecer la contraseña en forma hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Método para verificar la contraseña
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Crear todas las tablas definidas en la base de datos
db.create_all()


# Agregar el usuario inicial
if not User.query.filter_by(username='admin').first():
    admin_user = User(username='admin', email='estigarribiajose064@gmail.com', password='password', profile='Administrador')
    db.session.add(admin_user)
    db.session.commit()

# Agregar géneros literarios por defecto
default_genres = [
    'Novela', 'Cuento', 'Poesía', 'Ensayo', 'Teatro', 'Ciencia Ficción', 'Fantasía',
    'Terror', 'Misterio', 'Romance', 'Aventura', 'Biografía', 'Autobiografía', 'Crónica',
    'Diario', 'Memorias', 'Fábula', 'Leyenda', 'Mitología', 'Sátira'
]
for genre_name in default_genres:
    if not Genre.query.filter_by(name=genre_name).first():
        new_genre = Genre(name=genre_name)
        db.session.add(new_genre)
db.session.commit()

@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.profile == 'Administrador':
            return render_template("inicio.html")
        else:
            return redirect(url_for('inicio_lectura'))
    return redirect(url_for('login'))

@app.route('/inicio_lectura')
def inicio_lectura():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.profile == 'Lectura':
        return render_template("inicio_lectura.html")
    return redirect(url_for('home'))

@app.route('/biblioteca')
def biblioteca():
    if 'user_id' in session:
        search_query = request.args.get('search')
        if search_query:
            all_books = Book.query.filter(Book.title.contains(search_query)).all()
        else:
            all_books = Book.query.all()
        return render_template("index.html", books=all_books)
    return redirect(url_for('login'))

@app.route("/add", methods=["GET", "POST"])
def add():
    if 'user_id' not in session or User.query.get(session['user_id']).profile != 'Administrador':
        return redirect(url_for('login'))
    if request.method == "POST":
        title = request.form['title']
        author_id = request.form['author']
        genre_id = request.form['genre']
        rating = request.form['rating']
        year = request.form['year']
        publisher_name = request.form['publisher']
        
        publisher = Publisher.query.filter_by(name=publisher_name).first()
        if not publisher:
            publisher = Publisher(name=publisher_name)
            db.session.add(publisher)
        
        new_book = Book(title=title, author_id=author_id, genre_id=genre_id, rating=rating, year=year, publisher=publisher)
        db.session.add(new_book)
        db.session.commit()

        # Actualizar la cantidad de libros del autor
        author = Author.query.get(author_id)
        author.book_count = Book.query.filter_by(author_id=author_id).count()
        db.session.commit()

        return redirect(url_for('home'))
    
    authors = Author.query.all()
    genres = Genre.query.all()
    return render_template("add.html", authors=authors, genres=genres)

@app.route('/edit/<int:id>', methods=["GET", "POST"])
def edit_book(id):
    if 'user_id' not in session or User.query.get(session['user_id']).profile != 'Administrador':
        return redirect(url_for('login'))
    book = Book.query.get(id)
    if request.method == "POST":
        book.title = request.form["title"]
        book.author_id = request.form["author"]
        book.genre_id = request.form["genre"]
        book.rating = request.form["rating"]
        book.year = request.form["year"]
        book.publisher = Publisher.query.filter_by(name=request.form["publisher"]).first()
        db.session.commit()

        # Actualizar la cantidad de libros del autor
        author = Author.query.get(book.author_id)
        author.book_count = Book.query.filter_by(author_id=book.author_id).count()
        db.session.commit()

        return redirect(url_for('home'))
    
    authors = Author.query.all()
    genres = Genre.query.all()
    return render_template("edit.html", book=book, authors=authors, genres=genres)
=======
# Ruta para la página principal
@app.route('/')
def home():
    all_books = Book.query.all()
    return render_template('index.html', books=all_books)

# Ruta para la página de agregar libro
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        rating = request.form['rating']
        new_book = Book(title=title, author=author, rating=rating)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html')

# Ruta para la página de editar calificación
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_rating(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.rating = request.form['new_rating']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', book=book)


# Ruta para la página de eliminar libro
@app.route('/delete/<int:id>')
def delete_book(id):

    if 'user_id' not in session or User.query.get(session['user_id']).profile != 'Administrador':
        return redirect(url_for('login'))
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()

    # Actualizar la cantidad de libros del autor
    author = Author.query.get(book.author_id)
    author.book_count = Book.query.filter_by(author_id=book.author_id).count()
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_user = User(username=username, email=email, password=password, profile='Lectura')
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['profile'] = user.profile
            return redirect(url_for('home'))
        else:
            return "Usuario o contraseña incorrectos"
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/loan/<int:book_id>', methods=["GET", "POST"])
def loan_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    book = Book.query.get(book_id)
    if request.method == "POST":
        return_date = datetime.strptime(request.form['return_date'], '%Y-%m-%d')
        if return_date > datetime.utcnow() + timedelta(days=30):
            return "La fecha de devolución no puede ser mayor a un mes desde hoy."
        new_loan = Loan(book_id=book_id, user_id=session['user_id'], return_date=return_date)
        db.session.add(new_loan)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("loan.html", book=book)

@app.route('/loans')
def loans():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.profile == 'Administrador':
        all_loans = Loan.query.all()
    else:
        all_loans = Loan.query.filter_by(user_id=user.id).all()
    return render_template("loans.html", loans=all_loans)

@app.route('/return_book/<int:loan_id>')
def return_book(loan_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    loan = Loan.query.get(loan_id)
    loan.status = 'Devuelto'
    db.session.commit()
    return redirect(url_for('loans'))

@app.route('/register_author', methods=["GET", "POST"])
def register_author():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        name = request.form['name']
        nationality = request.form['nationality']
        birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
        gender = request.form['gender']
        genre_id = request.form['genre']
        new_author = Author(name=name, nationality=nationality, birth_date=birth_date, gender=gender, genre_id=genre_id)
        db.session.add(new_author)
        db.session.commit()
        return redirect(url_for('home'))
    genres = Genre.query.all()
    return render_template("register_author.html", genres=genres)

@app.route('/add_review/<int:book_id>', methods=["GET", "POST"])
def add_review(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    book = Book.query.get(book_id)
    if request.method == "POST":
        rating = request.form['rating']
        review = request.form['review']
        new_review = BookReview(book_id=book_id, user_id=session['user_id'], rating=rating, review=review)
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for('view_reviews', book_id=book_id))
    return render_template("add_review.html", book=book)

@app.route('/view_reviews/<int:book_id>')
def view_reviews(book_id):
    book = Book.query.get(book_id)
    reviews = BookReview.query.filter_by(book_id=book_id).all()
    return render_template("view_reviews.html", book=book, reviews=reviews)

if __name__ == "__main__":
    app.run(debug=True)
=======
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('home'))

# Ruta para la página de registro de usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Verificar si el usuario ya existe en la base de datos
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Ya existe un usuario con ese nombre de usuario. Por favor, elige otro."

        # Crear un nuevo usuario
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        # Añadir el nuevo usuario a la base de datos
        db.session.add(new_user)
        db.session.commit()


        # Redirigir a la página de inicio de sesión u otra página según tu flujo de la aplicación
        return redirect(url_for('home'))

    # Renderizar el formulario de registro
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
