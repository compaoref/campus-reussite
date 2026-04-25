import sqlite3
import os

# Créer campus.db dans le dossier courant
DB_PATH = "campus.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Créer les tables
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

# Insérer des données de test
cursor.execute('''
    INSERT INTO utilisateurs (nom, prenom, email, username, password, status)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('Dupont', 'Jean', 'jean@test.com', 'jdupont', 'pass123', 'actif'))

cursor.execute('''
    INSERT INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', ('Quelle est la capitale de la France ?', 'Londres', 'Paris', 'Rome', 'Berlin', 'Paris', 'La capitale est Paris.', 'Géographie'))

cursor.execute('''
    INSERT INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', ('2 + 2 = ?', '3', '4', '2', '22', '4', 'Addition basique', 'Maths'))

cursor.execute('''
    INSERT INTO feedback (email, titre, message, type)
    VALUES (?, ?, ?, ?)
''', ('jean@test.com', 'Super contenu', 'Très bon cours', 'Suggestion'))

conn.commit()
conn.close()

print(f"✅ Base de données créée: {DB_PATH}")
