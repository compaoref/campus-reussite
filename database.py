import sqlite3
import os
import sys
from datetime import datetime

# --- CHEMIN ABSOLU GARANTI ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "campus.db")

print(f"[DATABASE] Chemin de la DB: {DB_PATH}", file=sys.stderr)

class Database:
    def __init__(self):
        self.init_db()
    
    def get_connection(self):
        """Connexion à la DB"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialiser la DB"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS utilisateurs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    status TEXT DEFAULT 'actif',
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Quiz
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quiz (
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
                )
            ''')
            
            # Quiz Pending
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quiz_pending (
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
                )
            ''')
            
            # Feedback
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    titre TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT NOT NULL,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"[DATABASE] Initialized: {DB_PATH}", file=sys.stderr)
        except Exception as e:
            print(f"[DATABASE ERROR] {e}", file=sys.stderr)
    
    # --- UTILISATEURS ---
    def add_user(self, nom, prenom, email, username, password):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO utilisateurs (nom, prenom, email, username, password, status, date_creation)
                VALUES (?, ?, ?, ?, ?, 'actif', ?)
            ''', (nom, prenom, email, username, password, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            print(f"[DATABASE] User added: {email}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[DATABASE ERROR] add_user: {e}", file=sys.stderr)
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
            print(f"[DATABASE ERROR] get_user_by_email: {e}", file=sys.stderr)
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
            print(f"[DATABASE] Loaded {len(users)} users", file=sys.stderr)
            return users
        except Exception as e:
            print(f"[DATABASE ERROR] get_all_users: {e}", file=sys.stderr)
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
            print(f"[DATABASE ERROR] update_user_status: {e}", file=sys.stderr)
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
            print(f"[DATABASE ERROR] delete_user: {e}", file=sys.stderr)
            return False
    
    # --- QUIZ ---
    def add_quiz(self, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie))
            conn.commit()
            conn.close()
            print(f"[DATABASE] Quiz added: {question[:50]}...", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[DATABASE ERROR] add_quiz: {e}", file=sys.stderr)
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
            print(f"[DATABASE] Loaded {len(quiz)} quiz", file=sys.stderr)
            return quiz
        except Exception as e:
            print(f"[DATABASE ERROR] get_all_quiz: {e}", file=sys.stderr)
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
            print(f"[DATABASE ERROR] get_quiz_count: {e}", file=sys.stderr)
            return 0
    
    # --- QUIZ PENDING ---
    def add_pending_quiz(self, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quiz_pending (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[DATABASE ERROR] add_pending_quiz: {e}", file=sys.stderr)
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
            print(f"[DATABASE] Loaded {len(quiz)} pending quiz", file=sys.stderr)
            return quiz
        except Exception as e:
            print(f"[DATABASE ERROR] get_pending_quiz: {e}", file=sys.stderr)
            return []
    
    def approve_pending_quiz(self, pending_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM quiz_pending WHERE id = ?', (pending_id,))
            row = cursor.fetchone()
            
            if row:
                cursor.execute('''
                    INSERT INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (row['question'], row['option_a'], row['option_b'], row['option_c'], row['option_d'], row['reponses_correctes'], row['explication'], row['categorie']))
                
                cursor.execute('DELETE FROM quiz_pending WHERE id = ?', (pending_id,))
            
            conn.commit()
            conn.close()
            print(f"[DATABASE] Quiz approved: {pending_id}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[DATABASE ERROR] approve_pending_quiz: {e}", file=sys.stderr)
            return False
    
    def reject_pending_quiz(self, pending_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM quiz_pending WHERE id = ?', (pending_id,))
            conn.commit()
            conn.close()
            print(f"[DATABASE] Quiz rejected: {pending_id}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[DATABASE ERROR] reject_pending_quiz: {e}", file=sys.stderr)
            return False
    
    def update_pending_quiz(self, pending_id, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE quiz_pending 
                SET question = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, reponses_correctes = ?, explication = ?, categorie = ?
                WHERE id = ?
            ''', (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, pending_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[DATABASE ERROR] update_pending_quiz: {e}", file=sys.stderr)
            return False
    
    # --- FEEDBACK ---
    def add_feedback(self, email, titre, message, type_feedback):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (email, titre, message, type, date_creation)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, titre, message, type_feedback, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            print(f"[DATABASE] Feedback added: {email}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"[DATABASE ERROR] add_feedback: {e}", file=sys.stderr)
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
            print(f"[DATABASE] Loaded {len(feedback)} feedback", file=sys.stderr)
            return feedback
        except Exception as e:
            print(f"[DATABASE ERROR] get_all_feedback: {e}", file=sys.stderr)
            return []

# --- INSTANCE GLOBALE ---
db = Database()
