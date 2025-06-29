from flask import Flask, render_template, request, redirect, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import date
import os

app = Flask(__name__)

# Load config
app.config.from_pyfile('config.py')

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    return render_template("index.html", books=books)

@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (title, author))
        mysql.connection.commit()
        return redirect('/')
    return render_template("add_book.html")

@app.route('/delete/<int:id>')
def delete_book(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM books WHERE id = %s", [id])
    mysql.connection.commit()
    return redirect('/')

@app.route('/borrow-book', methods=['GET', 'POST'])
def borrow_book():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title FROM books WHERE available = TRUE")
    books = cur.fetchall()
    cur.execute("SELECT id, name FROM members")
    members = cur.fetchall()

    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        borrow_date = request.form['borrow_date']
        return_date = request.form['return_date']
        cur.execute("INSERT INTO borrow (book_id, member_id, borrow_date, return_date) VALUES (%s, %s, %s, %s)",
                    (book_id, member_id, borrow_date, return_date))
        cur.execute("UPDATE books SET available = FALSE WHERE id = %s", [book_id])
        mysql.connection.commit()
        return redirect('/')
    
    return render_template("borrow_book.html", books=books, members=members)

@app.route('/calculate-fine/<int:borrow_id>')
def calculate_fine(borrow_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT return_date FROM borrow WHERE id = %s", [borrow_id])
    return_date = cur.fetchone()[0]
    today = date.today()
    days_late = (today - return_date).days
    fine = 5 * max(0, days_late)
    return f"Fine: ₹{fine}"

@app.route('/api/books')
def api_books():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books")
    data = cur.fetchall()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
