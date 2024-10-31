from flask import Flask, jsonify, request, send_from_directory
import MySQLdb
from config import config
app = Flask(__name__)
def create_connection():
    try:
        connection = MySQLdb.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            passwd=config.MYSQL_PASSWORD,
            db=config.MYSQL_DB
        )
        print("Connected to MySQL database")
        return connection
    except MySQLdb.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None
def validate_incident_data(data):
    if not data:
        return None, "No data provided"
    required_fields = ['location', 'description']
    for field in required_fields:
        if field not in data or not data[field]:
            return None, f"Missing required field: {field}"
    clean_data = {
        'location': data['location'].strip(),
        'description': data['description'].strip(),
        'severity_level': int(data.get('severity_level', 1)),
        'image_url': data.get('image_url', '').strip() or None
    }
    return clean_data, None
@app.route('/')
def home():
    return send_from_directory('../frontend', 'homepage.html')
@app.route('/report')
def report():
    return send_from_directory('../frontend', 'index.html')
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)
@app.route('/api/report-incident', methods=['POST'])
def report_incident():
    try:
        data = request.get_json()
        print("Received data:", data)
        clean_data, error = validate_incident_data(data)
        if error:
            return jsonify({"message": error}), 400
        connection = create_connection()
        if connection is None:
            return jsonify({"message": "Database connection failed."}), 500
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO incidents (location, description, severity_level, image_url)
        VALUES (%s, %s, %s, %s)
        """
        values = (
            clean_data['location'],
            clean_data['description'],
            clean_data['severity_level'],
            clean_data['image_url']
        )
        print("Inserting values:", values)
        cursor.execute(insert_query, values)
        connection.commit()
        return jsonify({
            "message": "Incident reported successfully",
            "data": clean_data
        }), 201
    except MySQLdb.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "A database error occurred."}), 500
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"message": f"An error occurred while processing the request: {str(e)}"}), 500
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()
@app.route('/api/get-reports', methods=['GET'])
def get_reports():
    connection = create_connection()
    if connection is None:
        return jsonify({"message": "Database connection failed."}), 500
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM incidents ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        reports = []
        for row in rows:
            report = {}
            for i, value in enumerate(row):
                report[columns[i]] = value
            reports.append(report)
        return jsonify({"reports": reports}), 200
    except MySQLdb.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "A database error occurred."}), 500
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"message": "An error occurred while fetching reports."}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()
if __name__ == '__main__':
    app.run(debug=True)