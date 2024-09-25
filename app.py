from flask import Flask, render_template, request, url_for, redirect, flash, send_file, send_from_directory, Response
import csv
import os

from flask_sqlalchemy import SQLAlchemy
from itertools import zip_longest
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)

app.secret_key = 'SECRET_KEY'

class Config(object):
    if os.getenv('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').replace("postgres://", "postgresql://", 1)
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASEDIR, 'instance', 'books.db')}"


class Book(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    list_choice = db.Column(db.String(25), nullable=False)

    def __repr__(self):
        return f"{self.title}, {self.list_choice}"


@app.cli.command('init_db')
def initialize_database():
    """Initialize the database."""
    db.drop_all()
    db.create_all()
    echo('Initialized the database!')

@app.route("/", methods=['GET', 'POST'])
def index():
    books = Book.query.all()
    toread = Book.query.filter(Book.list_choice == "To Read").all()
    reading = Book.query.filter(Book.list_choice == "Reading").all()
    read = Book.query.filter(Book.list_choice == "Read").all()

    return render_template('index.html', books=books, toread=toread,reading=reading, read=read)


@app.route("/download", methods=['GET', 'POST'])
def download():
    toread = Book.query.filter(Book.list_choice == "To Read").all()
    reading = Book.query.filter(Book.list_choice == "Reading").all()
    read = Book.query.filter(Book.list_choice == "Read").all()

    toreadlist = []
    readinglist = []
    readlist = []

    for book in toread:
        toreadlist.append(book.title)
    for book in reading:
        readinglist.append(book.title)
    for book in read:
        readlist.append(book.title)

    path = './static/'

    if (len(toreadlist) == 0 and len(readinglist) == 0 and len(readlist) == 0):
        flash('No lists to download, add some books!')
        return redirect(url_for('index'))

    else:
        with open(path + 'all-books.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['To Read', 'Reading', 'Read'])
            writer.writerows(zip_longest(toreadlist, readinglist, readlist))

        return send_from_directory('./static', 'all-books.csv', as_attachment=True)


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.form:
        book = Book(title=request.form.get("title").title(), list_choice =request.form.get("list_choice"))
        titlecheck = book.query.filter_by(title=book.title).first()

        if titlecheck:
            flash('Book already exists on a shelf')
        else:
            db.session.add(book)
            db.session.commit()
            return redirect(url_for('index'))

    books = Book.query.all()

    return render_template('add.html', books=books)

@app.route('/edit/<int:id>/', methods=['GET','POST'])
def edit(id):
    book = Book.query.get_or_404(id)

    if request.method == "POST":
        title = request.form.get('title').title()
        list_choice = request.form.get('list_choice')

        book.title = title
        book.list_choice = list_choice

        db.session.add(book)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', book=book)

@app.post('/delete/<int:id>/')
def delete(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
