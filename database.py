import sqlite3
import os
import traceback
from datetime import datetime

# Lire DATABASE_PATH depuis la variable d'environnement ou depuis st.secrets (si Streamlit)
try:
    import streamlit as _st  # import protégé pour fonctionner hors Streamlit aussi
    streamlit_db_path = _st.secrets.get("DATABASE_PATH") if hasattr(_st, "secrets") else None
except Exception:
    streamlit_db_path = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(SCRIPT_DIR, "campus.db")
DB_PATH = os.environ.get("DATABASE_PATH", streamlit_db_path or DEFAULT_DB_PATH)

class Database:
    def __init__(self):
        self.init_db()
    
    def _connect(self):
        """
        Connexion SQLite configurée :
        - timeout: attendre si DB verrouillée
        - check_same_thread=False: permis pour accès multi-thread léger (Streamlit)
        - WAL pour meilleure concurrence lecture/écriture
        """
        conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute('PRAGMA journal_mode=WAL;')
            conn.execute('PRAGMA foreign_keys = ON;')
        except Exception:
            pass
        return conn

    def init_db(self):
        """Créer les tables si nécessaire"""
        try:
            conn = self._connect()
            cursor = conn.cursor()
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                status TEXT DEFAULT 'actif',
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS quiz (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                reponses_correctes TEXT NOT NULL,
                explication TEXT NOT NULL,
                categorie TEXT NOT NULL,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_pending (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                reponses_correctes TEXT NOT NULL,
                explication TEXT NOT NULL,
                categorie TEXT NOT NULL,
                source_file TEXT,
                date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                titre TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Init DB error: {e}")
            traceback.print_exc()
    
    def get_connection(self):
        return self._connect()
    
    def add_user(self, nom, prenom, email, username, password):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO utilisateurs (nom, prenom, email, username, password, status, date_creation) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                          (nom, prenom, email, username, password, 'actif', datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"add_user error: {e}")
            traceback.print_exc()
            return False
    
    def get_user_by_email(self, email):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM utilisateurs WHERE email = ?', (email,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'id': row['id'],
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'email': row['email'],
                    'username': row['username'],
                    'password': row['password'],
                    'status': row['status'],
                    'date_creation': row['date_creation']
                }
            return None
        except Exception as e:
            print(f"get_user_by_email error: {e}")
            traceback.print_exc()
            return None
    
    def get_all_users(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM utilisateurs ORDER BY date_creation DESC')
            rows = cursor.fetchall()
            conn.close()
            users = []
            for row in rows:
                users.append({
                    'id': row['id'],
                    'nom': row['nom'],
                    'prenom': row['prenom'],
                    'email': row['email'],
                    'username': row['username'],
                    'password': row['password'],
                    'status': row['status'],
                    'date_creation': row['date_creation']
                })
            return users
        except Exception as e:
            print(f"get_all_users error: {e}")
            traceback.print_exc()
            return []
    
    def update_user_status(self, user_id, status):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE utilisateurs SET status = ? WHERE id = ?', (status, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"update_user_status error: {e}")
            traceback.print_exc()
            return False
    
    def delete_user(self, user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM utilisateurs WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"delete_user error: {e}")
            traceback.print_exc()
            return False
    
    def add_quiz(self, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                          (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"add_quiz error: {e}")
            traceback.print_exc()
            return False
    
    def get_all_quiz(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM quiz ORDER BY categorie, date_creation')
            rows = cursor.fetchall()
            conn.close()
            quiz = []
            for row in rows:
                quiz.append({
                    'id': row['id'],
                    'question': row['question'],
                    'option_a': row['option_a'],
                    'option_b': row['option_b'],
                    'option_c': row['option_c'],
                    'option_d': row['option_d'],
                    'reponses_correctes': row['reponses_correctes'],
                    'explication': row['explication'],
                    'categorie': row['categorie']
                })
            return quiz
        except Exception as e:
            print(f"get_all_quiz error: {e}")
            traceback.print_exc()
            return []
    
    def get_quiz_count(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM quiz')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"get_quiz_count error: {e}")
            traceback.print_exc()
            return 0
    
    def delete_quiz(self, quiz_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM quiz WHERE id = ?', (quiz_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"delete_quiz error: {e}")
            traceback.print_exc()
            return False
    
    def add_pending_quiz(self, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO quiz_pending (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                          (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"add_pending_quiz error: {e}")
            traceback.print_exc()
            return False
    
    def get_pending_quiz(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM quiz_pending ORDER BY date_import DESC')
            rows = cursor.fetchall()
            conn.close()
            quiz = []
            for row in rows:
                quiz.append({
                    'id': row['id'],
                    'question': row['question'],
                    'option_a': row['option_a'],
                    'option_b': row['option_b'],
                    'option_c': row['option_c'],
                    'option_d': row['option_d'],
                    'reponses_correctes': row['reponses_correctes'],
                    'explication': row['explication'],
                    'categorie': row['categorie'],
                    'source_file': row['source_file']
                })
            return quiz
        except Exception as e:
            print(f"get_pending_quiz error: {e}")
            traceback.print_exc()
            return []
    
    def approve_pending_quiz(self, pending_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM quiz_pending WHERE id = ?', (pending_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute('INSERT INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                              (row['question'], row['option_a'], row['option_b'], row['option_c'], row['option_d'], row['reponses_correctes'], row['explication'], row['categorie']))
                cursor.execute('DELETE FROM quiz_pending WHERE id = ?', (pending_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"approve_pending_quiz error: {e}")
            traceback.print_exc()
            return False
    
    def reject_pending_quiz(self, pending_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM quiz_pending WHERE id = ?', (pending_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"reject_pending_quiz error: {e}")
            traceback.print_exc()
            return False
    
    def update_pending_quiz(self, pending_id, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE quiz_pending SET question = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, reponses_correctes = ?, explication = ?, categorie = ? WHERE id = ?', 
                          (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, pending_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"update_pending_quiz error: {e}")
            traceback.print_exc()
            return False
    
    def add_feedback(self, email, titre, message, type_feedback):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO feedback (email, titre, message, type, date_creation) VALUES (?, ?, ?, ?, ?)', 
                          (email, titre, message, type_feedback, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"add_feedback error: {e}")
            traceback.print_exc()
            return False
    
    def get_all_feedback(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM feedback ORDER BY date_creation DESC')
            rows = cursor.fetchall()
            conn.close()
            feedback = []
            for row in rows:
                feedback.append({
                    'id': row['id'],
                    'email': row['email'],
                    'titre': row['titre'],
                    'message': row['message'],
                    'type': row['type'],
                    'date_creation': row['date_creation']
                })
            return feedback
        except Exception as e:
            print(f"get_all_feedback error: {e}")
            traceback.print_exc()
            return []
    
    def get_db_path(self):
        return DB_PATH


db = Database()
