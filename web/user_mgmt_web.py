import hashlib

from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="user_management"
)
cursor = db.cursor()


@app.route('/')
def welcome():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash the password before storing it in the database
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        cursor.execute("INSERT INTO register_users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, password_hash))
        db.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the entered password for comparison
        entered_password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        # Retrieve user from the database based on the entered username
        cursor.execute("SELECT * FROM register_users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user[3] == entered_password_hash:  # Check if the user exists and the passwords match
            # Store the user's ID in the session for authentication
            session['user_id'] = user[0]
            return redirect('/users')
        else:
            # Invalid login, redirect back to the login page
            return redirect('/login')

    return render_template('login.html')


@app.route('/users')
def index():
    # Fetch all records from the database
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    page = request.args.get('page', 1, type=int)
    return render_template('users.html', users=users, page=page)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        # Insert new record into the database
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        db.commit()
        return redirect('/users')
    return render_template('add.html')


@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit(user_id):
    # Fetch the record to be edited from the database
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        # Update the record in the database
        cursor.execute("UPDATE users SET name = %s, email = %s WHERE id = %s", (name, email, user_id))
        db.commit()
        return redirect('/users')
    return render_template('edit.html', user=user)


@app.route('/delete/<int:user_id>')
def delete(user_id):
    # Delete the record from the database
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    return redirect('/users')


if __name__ == '__main__':
    app.run(debug=True)
