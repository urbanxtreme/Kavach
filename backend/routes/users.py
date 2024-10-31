# backend/routes/users.py

from flask import Blueprint, request, jsonify
from flask_mysqldb import MySQL

# Initialize blueprint
users_blueprint = Blueprint('users', __name__)

# Initialize MySQL
mysql = MySQL()

@users_blueprint.route('/create-profile', methods=['POST'])
def create_profile():
    try:
        data = request.json
        name = data['name']
        email = data['email']
        phone = data['phone']
        emergency_contact = data['emergency_contact']

        # Database insert
        cursor = mysql.connection.cursor()
        query = "INSERT INTO users (name, email, phone, emergency_contact) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, phone, emergency_contact))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': 'User profile created successfully'}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error creating user profile'}), 500

@users_blueprint.route('/user-profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            user_profile = {
                'id': result[0],
                'name': result[1],
                'email': result[2],
                'phone': result[3],
                'emergency_contact': result[4]
            }
            return jsonify(user_profile), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error fetching user profile'}), 500
