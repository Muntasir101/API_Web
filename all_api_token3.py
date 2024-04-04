"""
Implement Bearer token.
Implement error handle for Bearer token invalid.
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
    database="user_management"
)
cursor = db.cursor()

# A simple dictionary to store valid tokens (you should use a more secure method in production)
# valid_tokens = {"your_actual_bearer_token": "user_id"}
valid_tokens = {"secretToken"}


@auth.verify_token
def verify_token(token):
    # Verify the token here
    return token in valid_tokens


@auth.error_handler
def auth_error():
    return jsonify({'error': 'Invalid Token.Unauthorized Access', 'code': 401}), 401


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
    try:
        # Fetch all records from the database
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        user_list = []
        for user in users:
            user_dict = {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'password': user[3]
            }
            user_list.append(user_dict)
        return jsonify(user_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users', methods=['POST'])
@auth.login_required
def add_user():
    """
    Add a new user to the system.

    This endpoint allows authenticated users to add a new user to the system.

    Parameters:
        None

    Request Body:
        - name (str): The name of the user.
        - email (str): The email address of the user.
        - password (str): The password of the user.

    Returns:
        A JSON response with the following format:
        - Success (201 Created):
            {
                "message": "User added successfully"
            }
        - Error (400 Bad Request):
            {
                "error": "No JSON data received"
            }
            or
            {
                "error": "Name, email, and password are required fields"
            }

    Raises:
        None
    """
    if not request.json:
        return jsonify({'error': 'No JSON data received'}), 400

    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required fields'}), 400

    # Insert new record into the database
    cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    db.commit()
    return jsonify({'message': 'User added successfully'}), 201



@app.route('/users/<int:user_id>', methods=['GET'])
@auth.login_required
def get_user(user_id):
    """
    Retrieve user information based on the provided user_id.

    Args:
        user_id (int): The unique identifier of the user.

    Returns:
        flask.Response: JSON response containing user information if found,
        otherwise a message indicating that the user was not found.
    """
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
    if not request.json:
        return jsonify({'error': 'No JSON data received'}), 400

    name = request.json.get('name')
    email = request.json.get('email')
    password = request.json.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required fields'}), 400

    # Update the record in the database
    cursor.execute("UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s",
                   (name, email, password, user_id))
    db.commit()
    return jsonify({'message': 'User updated successfully'}), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    """
    Delete a user based on the provided user_id.

    Args:
        user_id (int): The unique identifier of the user to be deleted.

    Returns:
        flask.Response: JSON response indicating the success of the deletion.
    """
    # Delete the record from the database
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    return jsonify({'message': 'User deleted successfully'}), 204



if __name__ == '__main__':
    app.run(debug=True, port=8000)
