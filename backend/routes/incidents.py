from flask import Blueprint, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
incidents_blueprint = Blueprint('incidents', __name__)
mysql = MySQL()
@incidents_blueprint.route('/report-incident', methods=['POST'])
def report_incident():
    try:
        data = request.json
        location = data['location']
        description = data['description']
        severity_level = data.get('severity_level', 1)
        image_url = data.get('image_url', None)
        cursor = mysql.connection.cursor()
        query = "INSERT INTO incidents (location, description, severity_level, image_url, timestamp) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (location, description, severity_level, image_url, datetime.now()))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'message': 'Incident reported successfully'}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error reporting incident'}), 500
@incidents_blueprint.route('/incidents', methods=['GET'])
def get_incidents():
    try:
        cursor = mysql.connection.cursor()
        query = "SELECT * FROM incidents ORDER BY timestamp DESC"
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        incidents = []
        for row in results:
            incidents.append({
                'id': row[0],
                'location': row[1],
                'description': row[2],
                'severity_level': row[3],
                'image_url': row[4],
                'timestamp': row[5]
            })
        return jsonify(incidents), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Error fetching incidents'}), 500