import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "campus_reussite.db"

def init_database():
    """Initialiser la base de données SQLite"""
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
    except sqlite3.IntegrityError:
        return False

def load_users():
    """Charger tous les utilisateurs"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT nom, prenom, email, username, password, status, date_creation FROM utilisateurs", conn)
        conn.close()
        return df.to_dict('records') if len(df) > 0 else []
    except:
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
        return True
    except Exception as e:
        print(f"Erreur quiz: {e}")
        return False

def load_quiz():
    """Charger tous les quiz"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT question, a, b, c, d, reponses_correctes, explication, categorie FROM quiz", conn)
        conn.close()
        return df if len(df) > 0 else None
    except:
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
        return True
    except Exception as e:
        print(f"Erreur feedback: {e}")
        return False

def load_feedback():
    """Charger tous les feedbacks"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT email, titre, message, type, date FROM feedback ORDER BY date DESC", conn)
        conn.close()
        return df if len(df) > 0 else None
    except:
        return None

def block_user(email):
    """Bloquer un utilisateur"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE utilisateurs SET status = 'bloqué' WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def unblock_user(email):
    """Débloquer un utilisateur"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE utilisateurs SET status = 'actif' WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def delete_user(email):
    """Supprimer un utilisateur"""
    init_database()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM utilisateurs WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return True
    except:
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
        
        conn.close()
        return True
    except:
        return False
