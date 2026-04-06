import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

DB_PATH = 'data/predictions.db'

def init_database():
    """Initialize the database with required tables."""
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            input_text TEXT NOT NULL,
            input_method TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            real_prob REAL NOT NULL,
            fake_prob REAL NOT NULL
        )
    ''')
    
    # Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER NOT NULL,
            rating TEXT NOT NULL,
            comment TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (prediction_id) REFERENCES predictions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_prediction(input_text: str, input_method: str, prediction: str, 
                     confidence: float, real_prob: float, fake_prob: float) -> int:
    """Insert a new prediction into the database. Returns the prediction ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Truncate input text for storage (keep first 5000 chars)
    truncated_text = input_text[:5000] if len(input_text) > 5000 else input_text
    
    cursor.execute('''
        INSERT INTO predictions (input_text, input_method, prediction, confidence, real_prob, fake_prob)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (truncated_text, input_method, prediction, confidence, real_prob, fake_prob))
    
    prediction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return prediction_id

def get_prediction_history(limit: int = 100, offset: int = 0) -> List[Dict]:
    """Retrieve prediction history with pagination."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, timestamp, input_text, input_method, prediction, confidence, real_prob, fake_prob
        FROM predictions
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def search_predictions(search_term: str, limit: int = 50) -> List[Dict]:
    """Search predictions by text content."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, timestamp, input_text, input_method, prediction, confidence, real_prob, fake_prob
        FROM predictions
        WHERE input_text LIKE ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (f'%{search_term}%', limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def filter_predictions(prediction_type: Optional[str] = None, 
                      input_method: Optional[str] = None,
                      min_confidence: Optional[float] = None,
                      limit: int = 100) -> List[Dict]:
    """Filter predictions by various criteria."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT id, timestamp, input_text, input_method, prediction, confidence, real_prob, fake_prob FROM predictions WHERE 1=1'
    params = []
    
    if prediction_type:
        query += ' AND prediction = ?'
        params.append(prediction_type)
    
    if input_method:
        query += ' AND input_method = ?'
        params.append(input_method)
    
    if min_confidence is not None:
        query += ' AND confidence >= ?'
        params.append(min_confidence)
    
    query += ' ORDER BY timestamp DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def insert_feedback(prediction_id: int, rating: str, comment: Optional[str] = None) -> int:
    """Insert feedback for a prediction. Returns feedback ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO feedback (prediction_id, rating, comment)
        VALUES (?, ?, ?)
    ''', (prediction_id, rating, comment))
    
    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return feedback_id

def get_feedback_stats() -> Dict:
    """Get statistics about feedback."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN rating = 'positive' THEN 1 ELSE 0 END) as positive,
            SUM(CASE WHEN rating = 'negative' THEN 1 ELSE 0 END) as negative
        FROM feedback
    ''')
    
    row = cursor.fetchone()
    conn.close()
    
    return {
        'total': row[0],
        'positive': row[1],
        'negative': row[2]
    }

def get_prediction_stats() -> Dict:
    """Get overall prediction statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN prediction = 'FAKE NEWS' THEN 1 ELSE 0 END) as fake_count,
            SUM(CASE WHEN prediction = 'REAL NEWS' THEN 1 ELSE 0 END) as real_count,
            AVG(confidence) as avg_confidence
        FROM predictions
    ''')
    
    row = cursor.fetchone()
    conn.close()
    
    return {
        'total': row[0] or 0,
        'fake_count': row[1] or 0,
        'real_count': row[2] or 0,
        'avg_confidence': row[3] or 0.0
    }

def get_recent_predictions_with_feedback(limit: int = 50) -> List[Dict]:
    """Get recent predictions with their feedback."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            p.id, p.timestamp, p.input_text, p.prediction, p.confidence,
            f.rating, f.comment, f.timestamp as feedback_time
        FROM predictions p
        LEFT JOIN feedback f ON p.id = f.prediction_id
        ORDER BY p.timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
