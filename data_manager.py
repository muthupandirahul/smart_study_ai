import sqlite3
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DATA_DIR, 'study_companion.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables. Removed demo seeds."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users Table with Password
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            roll_number TEXT,
            name TEXT,
            email TEXT,
            role TEXT DEFAULT 'student'
        )
    ''')
    
    # Topics Completed Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS topics_completed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            topic_id TEXT,
            UNIQUE(username, topic_id)
        )
    ''')
    
    # Quiz Scores Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            topic_id TEXT,
            score INTEGER,
            total INTEGER,
            timestamp TEXT,
            UNIQUE(username, topic_id)
        )
    ''')
    
    # Seed default user if none exists
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        c.execute('''
            INSERT INTO users (username, password, roll_number, name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('student', '1111', '1001', 'Default Student', 'student@college.edu', 'student'))
    
    conn.commit()
    conn.close()


def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_json(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def create_user(username, password, roll_number, name, email, role='student'):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password, roll_number, name, email, role) VALUES (?, ?, ?, ?, ?, ?)',
                     (username, password, roll_number, name, email, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                        (username, password)).fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def get_student_progress(username):
    conn = get_db_connection()
    completed_rows = conn.execute('SELECT topic_id FROM topics_completed WHERE username = ?', (username,)).fetchall()
    topics_completed = [row['topic_id'] for row in completed_rows]
    
    score_rows = conn.execute('SELECT topic_id, score, total, timestamp FROM quiz_scores WHERE username = ?', (username,)).fetchall()
    quiz_scores = {}
    for row in score_rows:
        quiz_scores[row['topic_id']] = {
            "topic_id": row['topic_id'],
            "score": row['score'],
            "total": row['total'],
            "timestamp": row['timestamp']
        }
    conn.close()
    return {
        "topics_completed": topics_completed,
        "quiz_scores": quiz_scores,
        "syllabus_coverage": 0,
        "test_history": []
    }

def update_progress(username, topic_id, data_type, value):
    conn = get_db_connection()
    if data_type == 'complete':
        conn.execute('INSERT OR IGNORE INTO topics_completed (username, topic_id) VALUES (?, ?)', 
                     (username, topic_id))
    elif data_type == 'score':
        conn.execute('''
            INSERT OR REPLACE INTO quiz_scores (username, topic_id, score, total, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, topic_id, value['score'], value['total'], value.get('timestamp', str(datetime.now()))))
    conn.commit()
    conn.close()

def get_class_analytics():
    conn = get_db_connection()
    # Get all students and their scores
    students = conn.execute("SELECT username, name, roll_number FROM users WHERE role = 'student'").fetchall()
    
    analytics = []
    for std in students:
        username = std['username']
        scores = conn.execute('SELECT topic_id, score, total FROM quiz_scores WHERE username = ?', (username,)).fetchall()
        
        comp_count = conn.execute('SELECT COUNT(*) FROM topics_completed WHERE username = ?', (username,)).fetchone()[0]
        
        total_score = sum(s['score'] for s in scores)
        total_possible = sum(s['total'] for s in scores)
        avg_perf = (total_score / total_possible * 100) if total_possible > 0 else 0
        
        analytics.append({
            "name": std['name'],
            "roll": std['roll_number'],
            "completed": comp_count,
            "performance": int(avg_perf)
        })
    conn.close()
    return analytics

def update_db_schema_role():
    """Migration helper to add role column if missing"""
    conn = get_db_connection()
    try:
        conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'")
        conn.commit()
    except:
        pass # Already exists
    conn.close()

# Migration call
update_db_schema_role()

# Initialize DB on load
init_db()
