from flask import Flask, jsonify, request, send_from_directory
import MySQLdb
from config import config

app = Flask(__name__)

def create_connection():
    """Create a database connection using MySQLdb."""
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

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/report-incident', methods=['POST'])
def report_incident():
    connection = create_connection()
    if connection is None:
        return jsonify({"message": "Database connection failed."}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400

        cursor = connection.cursor()
        insert_query = """
        INSERT INTO incidents (location, description, severity_level, image_url)
        VALUES (%s, %s, %s, %s)
        """
        values = (
            data.get("location"),
            data.get("description"),
            data.get("severity_level"),
            data.get("image_url")
        )
        cursor.execute(insert_query, values)
        connection.commit()

        return jsonify({
            "message": "Incident reported successfully",
            "data": {
                "location": data.get("location"),
                "description": data.get("description"),
                "severity_level": data.get("severity_level"),
                "image_url": data.get("image_url")
            }
        }), 201

    except MySQLdb.Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "A database error occurred."}), 500
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"message": "An error occurred while processing the request."}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.route('/api/get-reports', methods=['GET'])
def get_reports():
    connection = create_connection()
    if connection is None:
        return jsonify({"message": "Database connection failed."}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM incidents")
        rows = cursor.fetchall()

        reports = []
        for row in rows:
            reports.append({
                "id": row[0],
                "location": row[1],
                "description": row[2],
                "severity_level": row[3],
                "image_url": row[4]
            })

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