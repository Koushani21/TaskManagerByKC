
from flask import Flask, request, jsonify, render_template
from flask_mysqldb import MySQL
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allow Netlify frontend to access backend

# MySQL Configuration (use Railway environment variables)
app.config['MYSQL_HOST'] = os.environ.get('MYSQLHOST', '127.0.0.1')
app.config['MYSQL_USER'] = os.environ.get('MYSQLUSER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQLPASSWORD', 'GUNGUN21')
app.config['MYSQL_DB'] = os.environ.get('MYSQLDATABASE', 'task_db')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQLPORT', 3306))

mysql = MySQL(app)

# Serve HTML
@app.route("/")
def index():
    return render_template("index.html")

# API Routes
@app.route("/test_db")
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return jsonify({"message": "Database connection successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, title, description, due_date, priority, category, status FROM tasks")
        data = cur.fetchall()
        cur.close()
        tasks = [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "dueDate": str(row[3]),
                "priority": row[4],
                "category": row[5],
                "status": row[6]
            } for row in data
        ]
        return jsonify(tasks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/addTask", methods=["POST"])
def add_task():
    try:
        data = request.json
        required_fields = ["title", "dueDate", "priority", "category", "status"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO tasks (title, description, due_date, priority, category, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data["title"], data.get("description", ""), data["dueDate"], data["priority"], data["category"], data["status"]))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Task added successfully"})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/updateTask/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        data = request.json
        required_fields = ["title", "dueDate", "priority", "category", "status"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE tasks
            SET title=%s, description=%s, due_date=%s, priority=%s, category=%s, status=%s
            WHERE id=%s
        """, (data["title"], data.get("description", ""), data["dueDate"], data["priority"], data["category"], data["status"], task_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Task updated successfully"})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/deleteTask/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Task deleted"})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Railway uses PORT env
    app.run(host='0.0.0.0', port=port, debug=True)
