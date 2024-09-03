from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Book(db.Model):
    id= db.Column(db.Integer, primary_key = True)
    book_title = db.Column(db.String(250), nullable=False)
    list_choice = db.Column(db.String(20))

    def __repr__(self):
        return f'Book: {self.book_title}, added to {self.list_choice}>'

@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/add/', methods=('GET','POST'))
def add():
    if request.method == 'POST':
        book_title = request.form['book_title']
        list_choice = request.form['list_choice']

        book = Book(book_title=book_title,list_choice=list_choice)
        db.session.add(book)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/<int:book_id>/edit/', methods=('GET', 'POST'))
def edit(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        book_title = request.form['book_title']
        list_choice = request.form['list_choice']

        book.book_title = book_title
        book.list_choice = list_choice

        db.session.add(book)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('edit.html', book=book)

@app.post('/<int:book_id>/delete/')
def delete(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
