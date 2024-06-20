from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-books-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CREAR TABLA

class books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'{self.title} - {self.author} - {self.rating}/10'

# Crear todas las tablas definidas en la base de datos
db.create_all()

@app.route('/')
def home():
    # Obtener todos los libros de la base de datos
    all_books_in_database = db.session.query(books).all()
    # Renderizar la plantilla "index.html" pasando la lista de libros
    return render_template("index.html", books=all_books_in_database)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # Recoger los datos del formulario (que estarán en forma de diccionario)
        data = request.form

        # Crear una nueva fila en la base de datos creando un objeto de la clase 'books'
        new_book = books(title=data['title'], author=data['author'], rating=data['rating'])

        # Agregar el libro a la base de datos
        db.session.add(new_book)
        db.session.commit()

        # Redirigir a la página principal
        return redirect(url_for('home'))
    # Renderizar la plantilla "add.html" para mostrar el formulario
    return render_template("add.html")

@app.route('/edit/<int:id>', methods=["GET", "POST"])
def edit_rating(id):
    if request.method == "POST":
        # Obtener el libro por su ID
        book_id = id
        book_to_update = books.query.get(book_id)
        print(book_to_update)
        # Actualizar la calificación del libro
        book_to_update.rating = request.form["new_rating"]
        db.session.commit()
        # Redirigir a la página principal
        return redirect(url_for('home'))
    # Obtener el libro por su ID para mostrar los detalles actuales en el formulario
    book = books.query.get(id)
    # Renderizar la plantilla "edit.html" pasando los datos del libro
    return render_template("edit.html", book_id=id, book=book)

@app.route('/delete/<int:id>')
def delete_book(id):
    # Obtener el libro por su ID
    book_id = id
    book_to_delete = books.query.get(book_id)
    # Eliminar el libro de la base de datos
    db.session.delete(book_to_delete)
    db.session.commit()
    # Redirigir a la página principal
    return redirect(url_for('home'))

if __name__ == "__main__":
    # Ejecutar la aplicación en modo depuración
    app.run(debug=True)

