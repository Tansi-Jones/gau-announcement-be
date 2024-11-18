from flask import Flask, request, jsonify
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)
DATABASE = 'announcement_system.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def generate_uuid():
    return str(uuid.uuid4())


def get_current_timestamp():
    """Get the current timestamp in 'YYYY-MM-DD HH:MM:SS' format."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


### USERS ENDPOINTS ###

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, name, email, role FROM Users').fetchall()
    conn.close()
    return jsonify([dict(row) for row in users])


@app.route('/users/<id>', methods=['GET'])
def get_user_by_id(id):
    conn = get_db_connection()
    user = conn.execute('SELECT id, name, email, role FROM Users WHERE id = ?', (id,)).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user))
    return jsonify({'message': 'User not found','type':'error'}), 404


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = generate_uuid()
    createdAt = get_current_timestamp()
    updated_at = createdAt
    try:
        conn = get_db_connection()
        conn.execute('''INSERT INTO Users (id, name, email, password, role, createdAt, updatedAt) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                     (user_id, data['name'], data['email'], data.get('password'), data['role'], createdAt, updated_at))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User created', 'type':'success'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Email already exists','type':'error'}), 400


@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    conn = get_db_connection()
    result = conn.execute('DELETE FROM Users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    if result.rowcount:
        return jsonify({'message': 'User deleted', 'type':'success'})
    return jsonify({'message': 'User not found', 'type':'error'}), 404


@app.route('/users/<id>', methods=['PATCH'])
def edit_user(id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided", 'type':'error'}), 400

    # Map valid fields to their corresponding column names
    valid_fields = {
        "name": "name",
        "email": "email",
        "password": "password",
        "role": "role"
    }

    # Filter out invalid fields and prepare the query
    fields_to_update = []
    values = []
    for field, column in valid_fields.items():
        if field in data:
            fields_to_update.append(f"{column} = ?")
            values.append(data[field])

    # Add updatedAt timestamp
    fields_to_update.append("updatedAt = CURRENT_TIMESTAMP")

    if not fields_to_update:
        return jsonify({"message": "No valid fields provided for update", 'type':'error'}), 400

    values.append(id)  # Add the user ID for the WHERE clause

    # Build the SQL query dynamically
    query = f"UPDATE Users SET {', '.join(fields_to_update)} WHERE id = ?"

    conn = get_db_connection()
    result = conn.execute(query, values)
    conn.commit()
    conn.close()

    if result.rowcount:
        return jsonify({"message": "User updated", 'type':'success'})
    return jsonify({"message": "User not found", 'type':'error'}), 404


@app.route('/users/login/<email>', methods=['GET'])
def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT id, name, email, role FROM Users WHERE email = ?', (email,)).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user))
    return jsonify({'message': 'User not found', 'type':'error'}), 404




### ANNOUNCEMENT ENDPOINTS ###

@app.route('/announcements', methods=['GET'])
def get_announcements():
    conn = get_db_connection()
    announcements = conn.execute('''
        SELECT 
            a.id, 
            a.title, 
            a.body, 
            a.startDate, 
            a.endDate, 
            a.image, 
            a.isUrgent, 
            u.name AS announcer,
            a.createdAt,
            a.updatedAt
        FROM Announcements a
        JOIN Users u ON a.announcerId = u.id
        ORDER BY a.isUrgent DESC, a.endDate ASC
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in announcements])


@app.route('/announcements/<id>', methods=['GET'])
def get_announcement_by_id(id):
    conn = get_db_connection()
    announcement = conn.execute('''
        SELECT a.id, a.title, a.body, a.startDate, a.endDate, a.image, a.isUrgent, u.name AS announcer
        FROM Announcements a
        JOIN Users u ON a.announcerId = u.id
        WHERE a.id = ?
    ''', (id,)).fetchone()
    conn.close()
    if announcement:
        return jsonify(dict(announcement))
    return jsonify({'message': 'Announcement not found', 'type':'error'}), 404


@app.route('/announcements', methods=['POST'])
def create_announcement():
    data = request.get_json()
    announcement_id = generate_uuid()
    createdAt = get_current_timestamp()
    updatedAt = createdAt
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO Announcements (id, title, body, image, startDate, endDate, isUrgent, announcerId, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (announcement_id, data['title'], data['body'], data.get('image'), data['startDate'], data['endDate'],
              data['isUrgent'], data['announcerId'], createdAt, updatedAt))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Announcement created', 'type':'success'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Invalid announcer ID or other constraints violated', 'type':'error'}), 400


@app.route('/announcements/<id>', methods=['DELETE'])
def delete_announcement(id):
    conn = get_db_connection()
    result = conn.execute('DELETE FROM Announcements WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    if result.rowcount:
        return jsonify({'message': 'Announcement deleted', 'type':'success'})
    return jsonify({'message': 'Announcement not found', 'type':'error'}), 404


@app.route('/announcements/<id>', methods=['PATCH'])
def edit_announcement(id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided", 'type':'error'}), 400

    # Map valid fields to their corresponding column names
    valid_fields = {
        "title": "title",
        "body": "body",
        "image": "image",
        "startDate": "startDate",
        "endDate": "endDate",
        "isUrgent": "isUrgent",
        "announcerId": "announcerId"
    }

    # Filter out invalid fields and prepare the query
    fields_to_update = []
    values = []
    for field, column in valid_fields.items():
        if field in data:
            fields_to_update.append(f"{column} = ?")
            values.append(data[field])

    # Add updatedAt timestamp
    fields_to_update.append("updatedAt = CURRENT_TIMESTAMP")

    if not fields_to_update:
        return jsonify({"message": "No valid fields provided for update", 'type':'error'}), 400

    values.append(id)  # Add the announcement ID for the WHERE clause

    # Build the SQL query dynamically
    query = f"UPDATE Announcements SET {', '.join(fields_to_update)} WHERE id = ?"

    conn = get_db_connection()
    result = conn.execute(query, values)
    conn.commit()
    conn.close()

    if result.rowcount:
        return jsonify({"message": "Announcement updated", 'type':'success'})
    return jsonify({"message": "Announcement not found", 'type':'error'}), 404



if __name__ == '__main__':
    app.run()
