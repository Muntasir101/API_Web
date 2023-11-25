"""
No Authentication method is implemented
"""

import hashlib
import secrets
from flask import Flask, request, jsonify, session
import mysql.connector
from flask_swagger import swagger

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="user_management"
)
cursor = db.cursor()


@app.route('/swagger')
def swagger_docs():
    swag = swagger(app)
    swag['info']['title'] = 'User Management API'
    swag['info']['version'] = '1.0'
    return jsonify(swag)


@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    # Hash the password before storing it in the database
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    cursor.execute("INSERT INTO register_users (username, email, password) VALUES (%s, %s, %s)",
                   (username, email, password_hash))
    db.commit()
    return jsonify({'message': 'User registered successfully'})


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    # Hash the entered password for comparison
    entered_password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Retrieve user from the database based on the entered username
    cursor.execute("SELECT * FROM register_users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and user[3] == entered_password_hash:  # Check if the user exists and the passwords match
        # Store the user's ID in the session for authentication
        session['user_id'] = user[0]
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid login credentials'})


@app.route('/users', methods=['GET'])
def get_all_users():
    """
        Get all users
        ---
        responses:
          200:
            description: List of users
        """
    # Fetch all records from the database
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    user_list = []
    for user in users:
        user_dict = {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'address':user[4]
        }
        user_list.append(user_dict)
    return jsonify(user_list)


@app.route('/users', methods=['POST'])
def add_user():
    name = request.json['name']
    email = request.json['email']
    # Insert new record into the database
    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
    db.commit()
    return jsonify({'message': 'User added successfully'})


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Fetch the record from the database
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        user_dict = {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'address': user[4]
        }
        return jsonify(user_dict)
    else:
        return jsonify({'message': 'User not found'})


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    name = request.json['name']
    email = request.json['email']
    # Update the record in the database
    cursor.execute("UPDATE users SET name = %s, email = %s WHERE id = %s", (name, email, user_id))
    db.commit()
    return jsonify({'message': 'User updated successfully'})


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Delete the record from the database
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    return jsonify({'message': 'User deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True, port=8000)
