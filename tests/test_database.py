import pytest
import sqlite3
import os
from unittest.mock import patch
import database

# Use an in-memory database for testing
TEST_DB_PATH = ':memory:'

@pytest.fixture
def mock_db_path():
    with patch('database.DB_PATH', TEST_DB_PATH):
        yield TEST_DB_PATH

@pytest.fixture
def db_conn(mock_db_path):
    # Initialize the tables using the mocked path
    with patch('database.sqlite3.connect') as mock_connect:
        # Actually use real sqlite3 but in-memory
        conn = sqlite3.connect(':memory:')
        mock_connect.return_value = conn
        
        # We need to run init_database, but replace os.makedirs to not create folders
        with patch('os.makedirs'):
            database.init_database()
        
        yield conn

def test_init_database(mock_db_path):
    with patch('os.makedirs') as mock_makedirs:
        with patch('database.sqlite3.connect') as mock_connect:
            conn = sqlite3.connect(':memory:')
            mock_connect.return_value = conn
            database.init_database()
            mock_makedirs.assert_called_once_with('data', exist_ok=True)
            
            # Verify tables exist
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='predictions'")
            assert cursor.fetchone() is not None
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
            assert cursor.fetchone() is not None

def test_insert_prediction(mock_db_path):
    with patch('database.sqlite3.connect') as mock_connect:
        conn = sqlite3.connect(':memory:')
        mock_connect.return_value = conn
        with patch('os.makedirs'):
            database.init_database()

        # Insert prediction
        pred_id = database.insert_prediction(
            input_text="Test news content",
            input_method="Text",
            prediction="FAKE NEWS",
            confidence=0.9,
            real_prob=0.1,
            fake_prob=0.9
        )
        assert pred_id == 1
        
        # Verify
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions WHERE id=?", (pred_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row[2] == "Test news content"

def test_insert_feedback(mock_db_path):
    with patch('database.sqlite3.connect') as mock_connect:
        conn = sqlite3.connect(':memory:')
        mock_connect.return_value = conn
        with patch('os.makedirs'):
            database.init_database()
            
        pred_id = database.insert_prediction("text", "method", "pred", 0.5, 0.5, 0.5)
        
        feedback_id = database.insert_feedback(pred_id, "positive", "Great!")
        assert feedback_id == 1
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback WHERE id=?", (feedback_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row[2] == "positive"
        assert row[3] == "Great!"

def test_get_prediction_stats(mock_db_path):
    with patch('database.sqlite3.connect') as mock_connect:
        conn = sqlite3.connect(':memory:')
        mock_connect.return_value = conn
        with patch('os.makedirs'):
            database.init_database()

        database.insert_prediction("text1", "method", "FAKE NEWS", 0.9, 0.1, 0.9)
        database.insert_prediction("text2", "method", "REAL NEWS", 0.8, 0.8, 0.2)
        
        stats = database.get_prediction_stats()
        assert stats['total'] == 2
        assert stats['fake_count'] == 1
        assert stats['real_count'] == 1
        assert stats['avg_confidence'] == 0.85
