"""
Database Manager for Historical Tracking
Manages SQLite database for session history and analytics.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import os

class SessionDatabase:
    """Manage learning session history in SQLite database."""
    
    def __init__(self, db_path="learning_sessions.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                total_time_seconds INTEGER,
                overall_score REAL,
                checkpoints_count INTEGER,
                passed_count INTEGER,
                feynman_used_count INTEGER,
                user_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Checkpoints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                checkpoint_index INTEGER,
                topic TEXT,
                subtopic TEXT,
                score REAL,
                passed BOOLEAN,
                feynman_used BOOLEAN,
                attempt_count INTEGER,
                time_spent_seconds INTEGER,
                questions_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # Questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkpoint_id INTEGER,
                question_text TEXT,
                answer_text TEXT,
                objective TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (checkpoint_id) REFERENCES checkpoints (checkpoint_id)
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                metric_name TEXT,
                metric_value REAL,
                metric_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_session(self, session_data):
        """
        Save complete session to database.
        
        Args:
            session_data (dict): Session information
                
        Returns:
            int: Session ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert session
            cursor.execute("""
                INSERT INTO sessions (
                    start_time, end_time, total_time_seconds, overall_score,
                    checkpoints_count, passed_count, feynman_used_count, user_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_data.get('start_time', datetime.now()),
                session_data.get('end_time', datetime.now()),
                session_data.get('total_time', 0),
                session_data.get('overall_score', 0.0),
                len(session_data.get('checkpoints', [])),
                sum(1 for cp in session_data.get('checkpoints', []) if cp.get('passed', False)),
                sum(1 for cp in session_data.get('checkpoints', []) if cp.get('feynman_used', False)),
                session_data.get('user_notes', '')
            ))
            
            session_id = cursor.lastrowid
            
            # Insert checkpoints
            for i, checkpoint in enumerate(session_data.get('checkpoints', [])):
                cursor.execute("""
                    INSERT INTO checkpoints (
                        session_id, checkpoint_index, topic, subtopic, score,
                        passed, feynman_used, attempt_count, time_spent_seconds, questions_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    i,
                    checkpoint.get('topic', ''),
                    checkpoint.get('subtopic', ''),
                    checkpoint.get('score', 0.0),
                    checkpoint.get('passed', False),
                    checkpoint.get('feynman_used', False),
                    checkpoint.get('attempt_count', 0),
                    checkpoint.get('time_spent', 0),
                    len(checkpoint.get('questions', []))
                ))
                
                checkpoint_id = cursor.lastrowid
                
                # Insert questions and answers
                questions = checkpoint.get('questions', [])
                answers = checkpoint.get('answers', [])
                
                for q, a in zip(questions, answers):
                    cursor.execute("""
                        INSERT INTO questions (
                            checkpoint_id, question_text, answer_text, objective
                        ) VALUES (?, ?, ?, ?)
                    """, (
                        checkpoint_id,
                        q.get('question', ''),
                        a.get('answer', ''),
                        q.get('objective', '')
                    ))
            
            conn.commit()
            return session_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_session_history(self, limit=10):
        """Get recent session history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                session_id, start_time, end_time, total_time_seconds,
                overall_score, checkpoints_count, passed_count, feynman_used_count
            FROM sessions
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            sessions.append({
                'session_id': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'total_time': row[3],
                'overall_score': row[4],
                'checkpoints_count': row[5],
                'passed_count': row[6],
                'feynman_used_count': row[7]
            })
        
        return sessions
    
    def get_performance_trends(self):
        """Get performance trends over time."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                date(created_at) as date,
                AVG(overall_score) as avg_score,
                COUNT(*) as session_count,
                AVG(total_time_seconds) as avg_time
            FROM sessions
            GROUP BY date(created_at)
            ORDER BY date DESC
            LIMIT 30
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        trends = []
        for row in rows:
            trends.append({
                'date': row[0],
                'avg_score': row[1],
                'session_count': row[2],
                'avg_time': row[3]
            })
        
        return trends
    
    def get_topic_mastery(self):
        """Get mastery level by topic."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                topic,
                COUNT(*) as attempts,
                AVG(score) as avg_score,
                SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed_count
            FROM checkpoints
            GROUP BY topic
            ORDER BY avg_score DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        mastery = []
        for row in rows:
            mastery.append({
                'topic': row[0],
                'attempts': row[1],
                'avg_score': row[2],
                'passed_count': row[3],
                'pass_rate': row[3] / row[1] if row[1] > 0 else 0
            })
        
        return mastery
    
    def get_statistics(self):
        """Get overall statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total sessions
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]
        
        # Average score
        cursor.execute("SELECT AVG(overall_score) FROM sessions")
        avg_score = cursor.fetchone()[0] or 0
        
        # Total time
        cursor.execute("SELECT SUM(total_time_seconds) FROM sessions")
        total_time = cursor.fetchone()[0] or 0
        
        # Total checkpoints
        cursor.execute("SELECT COUNT(*) FROM checkpoints")
        total_checkpoints = cursor.fetchone()[0]
        
        # Pass rate
        cursor.execute("SELECT AVG(CASE WHEN passed = 1 THEN 1.0 ELSE 0.0 END) FROM checkpoints")
        pass_rate = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_sessions': total_sessions,
            'avg_score': avg_score,
            'total_time_hours': total_time / 3600,
            'total_checkpoints': total_checkpoints,
            'pass_rate': pass_rate
        }
