import sqlite3
import uuid
from datetime import datetime

DATABASE = 'announcement_system.db'

def generate_uuid():
    """Generate a random UUID string."""
    return str(uuid.uuid4())

def get_current_timestamp():
    """Get the current timestamp in 'YYYY-MM-DD HH:MM:SS' format."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def create_tables():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Enable foreign key constraints in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create Users table with createdAt and updatedAt
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id TEXT PRIMARY KEY,  -- Random UUID
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT,  -- Optional, only for admins
            role TEXT NOT NULL CHECK (role IN ('Announcer', 'Admin')),
            createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Auto-created timestamp
            updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP   -- Auto-updated timestamp
        )
    ''')

    # Create Announcements table with createdAt and updatedAt
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Announcements (
            id TEXT PRIMARY KEY,  -- Random UUID
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            image TEXT,  -- Optional
            startDate DATE NOT NULL,
            endDate DATE NOT NULL,
            isUrgent BOOLEAN NOT NULL CHECK (isUrgent IN (0, 1)),
            announcerId TEXT NOT NULL,
            createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Auto-created timestamp
            updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Auto-updated timestamp
            FOREIGN KEY (announcerId) REFERENCES Users (id)
        )
    ''')

    # Create Archive table with createdAt and updatedAt
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Archive (
            id TEXT PRIMARY KEY,  -- Random UUID
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            image TEXT,  -- Optional
            startDate DATE NOT NULL,
            endDate DATE NOT NULL,
            announcerName TEXT NOT NULL,
            createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Auto-created timestamp
            updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP   -- Auto-updated timestamp
        )
    ''')

    conn.commit()
    conn.close()
    print("Tables created successfully!")

create_tables()
