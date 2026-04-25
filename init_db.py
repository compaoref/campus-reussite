import sqlite3
from datetime import datetime

db = sqlite3.connect("campus.db")
c = db.cursor()

# Créer tables
c.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    status TEXT DEFAULT 'actif',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

c.execute('''CREATE TABLE IF NOT EXISTS quiz (
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

c.execute('''CREATE TABLE IF NOT EXISTS quiz_pending (
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

c.execute('''CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    titre TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

# Ajouter données test
c.execute("INSERT OR IGNORE INTO utilisateurs (nom, prenom, email, username, password) VALUES (?, ?, ?, ?, ?)",
    ("Dupont", "Jean", "jean@test.com", "jdupont", "pass123"))

c.execute("INSERT OR IGNORE INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    ("Quelle est la capitale de la France ?", "Londres", "Paris", "Rome", "Berlin", "Paris", "La capitale est Paris.", "Géographie"))

c.execute("INSERT OR IGNORE INTO quiz (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    ("2 + 2 = ?", "3", "4", "2", "22", "4", "Addition basique", "Maths"))

c.execute("INSERT OR IGNORE INTO feedback (email, titre, message, type) VALUES (?, ?, ?, ?)",
    ("jean@test.com", "Super contenu", "Très bon cours", "Suggestion"))

db.commit()
db.close()

print("✅ campus.db créé et initialisé!")