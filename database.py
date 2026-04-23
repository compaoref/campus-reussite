import sqlite3
import os
from datetime import datetime
import json

DB_PATH = os.path.join(os.getcwd(), "campus.db")

class Database:
    """Gestionnaire SQLite pour Campus Réussite"""
    
    def __init__(self):
        self.init_db()
    
    def get_connection(self):
        """Obtenir connexion à la DB"""
        return sqlite3.connect(DB_PATH)
    
    def init_db(self):
        """Initialiser la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table Utilisateurs
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
        
        # Table Quiz
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
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'valide'
            )
        ''')
        
        # Table Quiz en Attente (Import)
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
                date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'en_attente'
            )
        ''')
        
        # Table Feedback
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                titre TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'nouveau'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # --- UTILISATEURS ---
    def add_user(self, nom, prenom, email, username, password):
        """Ajouter un utilisateur"""
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
        except sqlite3.IntegrityError:
            return False
    
    def get_user_by_email(self, email):
        """Obtenir un utilisateur par email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM utilisateurs WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'nom': result[1],
                'prenom': result[2],
                'email': result[3],
                'username': result[4],
                'password': result[5],
                'status': result[6],
                'date_creation': result[7]
            }
        return None
    
    def get_all_users(self):
        """Obtenir tous les utilisateurs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM utilisateurs ORDER BY date_creation DESC')
        results = cursor.fetchall()
        conn.close()
        
        users = []
        for row in results:
            users.append({
                'id': row[0],
                'nom': row[1],
                'prenom': row[2],
                'email': row[3],
                'username': row[4],
                'password': row[5],
                'status': row[6],
                'date_creation': row[7]
            })
        return users
    
    def update_user_status(self, user_id, status):
        """Mettre à jour le statut d'un utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE utilisateurs SET status = ? WHERE id = ?', (status, user_id))
        conn.commit()
        conn.close()
    
    def delete_user(self, user_id):
        """Supprimer un utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM utilisateurs WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    # --- QUIZ ---
    def add_quiz(self, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie):
        """Ajouter un quiz"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'valide')
            ''', (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False
    
    def get_all_quiz(self):
        """Obtenir tous les quiz valides"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM quiz WHERE status = "valide" ORDER BY categorie, date_creation')
        results = cursor.fetchall()
        conn.close()
        
        quiz = []
        for row in results:
            quiz.append({
                'id': row[0],
                'question': row[1],
                'option_a': row[2],
                'option_b': row[3],
                'option_c': row[4],
                'option_d': row[5],
                'reponses_correctes': row[6],
                'explication': row[7],
                'categorie': row[8],
                'date_creation': row[9],
                'status': row[10]
            })
        return quiz
    
    def get_quiz_count(self):
        """Nombre total de quiz"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM quiz WHERE status = "valide"')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    # --- QUIZ PENDING (IMPORT) ---
    def add_pending_quiz(self, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file):
        """Ajouter un quiz en attente"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quiz_pending (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'en_attente')
            ''', (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, source_file))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False
    
    def get_pending_quiz(self):
        """Obtenir tous les quiz en attente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM quiz_pending WHERE status = "en_attente" ORDER BY date_import DESC')
        results = cursor.fetchall()
        conn.close()
        
        quiz = []
        for row in results:
            quiz.append({
                'id': row[0],
                'question': row[1],
                'option_a': row[2],
                'option_b': row[3],
                'option_c': row[4],
                'option_d': row[5],
                'reponses_correctes': row[6],
                'explication': row[7],
                'categorie': row[8],
                'source_file': row[9],
                'date_import': row[10],
                'status': row[11]
            })
        return quiz
    
    def approve_pending_quiz(self, pending_id):
        """Approuver un quiz en attente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Récupérer les données
        cursor.execute('SELECT * FROM quiz_pending WHERE id = ?', (pending_id,))
        row = cursor.fetchone()
        
        if row:
            # Ajouter au table principale
            cursor.execute('''
                INSERT INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'valide')
            ''', (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
            
            # Supprimer de pending
            cursor.execute('DELETE FROM quiz_pending WHERE id = ?', (pending_id,))
        
        conn.commit()
        conn.close()
    
    def reject_pending_quiz(self, pending_id):
        """Rejeter un quiz en attente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM quiz_pending WHERE id = ?', (pending_id,))
        conn.commit()
        conn.close()
    
    def update_pending_quiz(self, pending_id, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie):
        """Modifier un quiz en attente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE quiz_pending 
            SET question = ?, option_a = ?, option_b = ?, option_c = ?, option_d = ?, reponses_correctes = ?, explication = ?, categorie = ?
            WHERE id = ?
        ''', (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie, pending_id))
        conn.commit()
        conn.close()
    
    # --- FEEDBACK ---
    def add_feedback(self, email, titre, message, type_feedback):
        """Ajouter un feedback"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (email, titre, message, type, status)
                VALUES (?, ?, ?, ?, 'nouveau')
            ''', (email, titre, message, type_feedback))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False
    
    def get_all_feedback(self):
        """Obtenir tous les feedbacks"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feedback ORDER BY date_creation DESC')
        results = cursor.fetchall()
        conn.close()
        
        feedback = []
        for row in results:
            feedback.append({
                'id': row[0],
                'email': row[1],
                'titre': row[2],
                'message': row[3],
                'type': row[4],
                'date_creation': row[5],
                'status': row[6]
            })
        return feedback
    
    def mark_feedback_as_read(self, feedback_id):
        """Marquer un feedback comme lu"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE feedback SET status = "lu" WHERE id = ?', (feedback_id,))
        conn.commit()
        conn.close()

# Instance globale
db = Database()
