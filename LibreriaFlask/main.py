from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-books-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'  # Clave secreta para proteger las sesiones y cookies
db = SQLAlchemy(app)

# Define el modelo de Libro
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'{self.title} - {self.author} - {self.rating}/10'

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
