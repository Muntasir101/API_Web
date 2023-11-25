"""
Implement Bearer token.
No error handle for Bearer token invalid.
"""

from flask import Flask, request, jsonify
from flask_swagger import swagger
from flask_httpauth import HTTPTokenAuth
import mysql.connector


app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

# Your database connection and cursor initialization
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="test_user_management"
)
cursor = db.cursor()

# A simple dictionary to store valid tokens (you should use a more secure method in production)
# valid_tokens = {"your_actual_bearer_token": "user_id"}
valid_tokens = {"secretToken": "user_id"}


@auth.verify_token
def verify_token(token):
    # Verify the token here
    return token in valid_tokens


@app.route('/swagger')
def swagger_docs():
    swag = swagger(app)
    swag['info']['title'] = 'User Management API'
    swag['info']['version'] = '1.0'
    return jsonify(swag)


@app.route('/users', methods=['GET'])
@auth.login_required
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
            'email': user[2]
        }
        user_list.append(user_dict)
    return jsonify(user_list)


@app.route('/users', methods=['POST'])
@auth.login_required
def add_user():
    name = request.json['name']
    email = request.json['email']
    # Insert new record into the database
    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
    db.commit()
    return jsonify({'message': 'User added successfully'})


@app.route('/users/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    # Fetch the record from the database
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        user_dict = {
            'id': user[0],
            'name': user[1],
            'email': user[2]
        }
        return jsonify(user_dict)
    else:
        return jsonify({'message': 'User not found'})


@app.route('/users/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    name = request.json['name']
    email = request.json['email']
    # Update the record in the database
    cursor.execute("UPDATE users SET name = %s, email = %s WHERE id = %s", (name, email, user_id))
    db.commit()
    return jsonify({'message': 'User updated successfully'})


@app.route('/users/<int:user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    # Delete the record from the database
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    return jsonify({'message': 'User deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True, port=8000)
