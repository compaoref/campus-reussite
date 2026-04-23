import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = "campus_reussite.db"

def init_database():
    """Initialiser la base de données SQLite"""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Table utilisateurs
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
        
        # Table quiz
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                a TEXT NOT NULL,
                b TEXT NOT NULL,
                c TEXT NOT NULL,
                d TEXT NOT NULL,
                reponses_correctes TEXT NOT NULL,
                explication TEXT,
                categorie TEXT,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table feedback
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                titre TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

def save_user(user_data):
    """Enregistrer un utilisateur"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO utilisateurs (nom, prenom, email, username, password, status, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['nom'],
            user_data['prenom'],
            user_data['email'],
            user_data['username'],
            user_data['password'],
            user_data.get('status', 'actif'),
            user_data.get('date_creation', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Erreur: Email ou username déjà utilisé - {e}")
        return False
    except Exception as e:
        print(f"Erreur save_user: {e}")
        return False

def load_users():
    """Charger tous les utilisateurs"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT nom, prenom, email, username, password, status, date_creation FROM utilisateurs ORDER BY date_creation DESC")
        rows = cursor.fetchall()
        conn.close()
        
        result = [dict(row) for row in rows] if rows else []
        return result
    except Exception as e:
        print(f"Erreur load_users: {e}")
        return []

def add_quiz(question, a, b, c, d, correct, explication, categorie):
    """Ajouter un quiz"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO quiz (question, a, b, c, d, reponses_correctes, explication, categorie)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (question, a, b, c, d, correct, explication, categorie))
        conn.commit()
        conn.close()
        print(f"✅ Quiz ajouté: {question}")
        return True
    except Exception as e:
        print(f"Erreur add_quiz: {e}")
        return False

def load_quiz():
    """Charger tous les quiz"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT question, a, b, c, d, reponses_correctes, explication, categorie FROM quiz ORDER BY date_creation DESC",
            conn
        )
        conn.close()
        
        if len(df) > 0:
            return df
        else:
            return None
    except Exception as e:
        print(f"Erreur load_quiz: {e}")
        return None

def save_feedback(feedback_data):
    """Enregistrer un feedback"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO feedback (email, titre, message, type, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            feedback_data['email'],
            feedback_data['titre'],
            feedback_data['message'],
            feedback_data['type'],
            feedback_data.get('date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ))
        conn.commit()
        conn.close()
        print(f"✅ Feedback enregistré: {feedback_data['titre']}")
        return True
    except Exception as e:
        print(f"Erreur save_feedback: {e}")
        return False

def load_feedback():
    """Charger tous les feedbacks"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT email, titre, message, type, date FROM feedback ORDER BY date DESC",
            conn
        )
        conn.close()
        
        if len(df) > 0:
            return df
        else:
            return None
    except Exception as e:
        print(f"Erreur load_feedback: {e}")
        return None

def delete_user(email):
    """Supprimer un utilisateur"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM utilisateurs WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        print(f"✅ Utilisateur supprimé: {email}")
        return True
    except Exception as e:
        print(f"Erreur delete_user: {e}")
        return False

def toggle_user_status(email):
    """Basculer le statut d'un utilisateur (actif <-> bloqué)"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM utilisateurs WHERE email = ?", (email,))
        result = cursor.fetchone()
        
        if result:
            new_status = 'actif' if result[0] == 'bloqué' else 'bloqué'
            cursor.execute("UPDATE utilisateurs SET status = ? WHERE email = ?", (new_status, email))
            conn.commit()
            print(f"✅ Statut changé: {email} -> {new_status}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur toggle_user_status: {e}")
        return False

def check_quiz_exists(question):
    """Vérifier si un quiz existe déjà"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM quiz WHERE question = ?", (question,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"Erreur check_quiz_exists: {e}")
        return False

def clear_all_quizzes():
    """Supprimer tous les quiz (utilisé avant import)"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quiz")
        conn.commit()
        conn.close()
        print("✅ Tous les quiz supprimés")
        return True
    except Exception as e:
        print(f"Erreur clear_all_quizzes: {e}")
        return False
