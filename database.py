import sqlite3
import os
from datetime import datetime

# Le chemin de la DB est toujours dans le même dossier que ce script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "campus.db")

class Database:
    def get_db_path(self):
        return DB_PATH

    def get_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
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
            return True
        except Exception as e:
            print(f"Erreur add_user: {e}")
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
            print(f"Erreur get_user_by_email: {e}")
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
            print(f"Erreur get_all_users: {e}")
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
            print(f"Erreur update_user_status: {e}")
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
            print(f"Erreur delete_user: {e}")
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
            return True
        except Exception as e:
            print(f"Erreur add_quiz: {e}")
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
            print(f"Erreur get_all_quiz: {e}")
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
            print(f"Erreur get_quiz_count: {e}")
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
            print(f"Erreur add_pending_quiz: {e}")
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
            print(f"Erreur get_pending_quiz: {e}")
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
            return True
        except Exception as e:
            print(f"Erreur approve_pending_quiz: {e}")
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
            print(f"Erreur reject_pending_quiz: {e}")
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
            print(f"Erreur update_pending_quiz: {e}")
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
            return True
        except Exception as e:
            print(f"Erreur add_feedback: {e}")
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
            print(f"Erreur get_all_feedback: {e}")
            return []

# Instance globale
db = Database()
