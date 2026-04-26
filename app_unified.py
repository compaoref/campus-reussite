"""
🎓 CAMPUS RÉUSSITE v7.0
Application Professionnelle - Séries de Quizzes + Admin Caché + Gestion Utilisateurs
"""

import streamlit as st
import sqlite3
import pandas as pd
import re
import os
from datetime import datetime
from pathlib import Path

# ========== CONFIG PAGE ==========
st.set_page_config(
    page_title="Campus Réussite",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = os.path.join(os.path.dirname(__file__), "campus.db")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo_campus_reussite.jpg")

# ========== DATABASE ==========
class Database:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Table utilisateurs
        cursor.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'apprenant',
            status TEXT DEFAULT 'actif',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Table séries
        cursor.execute('''CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            description TEXT,
            nombre_questions INTEGER DEFAULT 50,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Table quiz
        cursor.execute('''CREATE TABLE IF NOT EXISTS quiz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            reponses_correctes TEXT NOT NULL,
            explication TEXT NOT NULL,
            ordre INTEGER,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (series_id) REFERENCES series(id)
        )''')
        
        # Table quiz_pending
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
        
        # Table résultats (quand utilisateur valide une série)
        cursor.execute('''CREATE TABLE IF NOT EXISTS resultats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            series_id INTEGER NOT NULL,
            score INTEGER,
            total INTEGER,
            pourcentage REAL,
            date_completion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id),
            FOREIGN KEY (series_id) REFERENCES series(id)
        )''')
        
        # Table feedback
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
    
    def query(self, sql, params=()):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
    
    def fetch_one(self, sql, params=()):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def fetch_all(self, sql, params=()):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]

db = Database()

# ========== FONCTIONS UTILITAIRES ==========
def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def add_user(nom, prenom, email, username, password):
    try:
        db.query('INSERT INTO utilisateurs (nom, prenom, email, username, password, role) VALUES (?, ?, ?, ?, ?, ?)',
                (nom, prenom, email, username, password, 'apprenant'))
        return True
    except:
        return False

def get_user_by_email(email):
    return db.fetch_one('SELECT * FROM utilisateurs WHERE email = ?', (email,))

def add_series(nom, description, nombre_questions=50):
    try:
        db.query('INSERT INTO series (nom, description, nombre_questions) VALUES (?, ?, ?)',
                (nom, description, nombre_questions))
        return True
    except:
        return False

def get_all_series():
    return db.fetch_all('SELECT * FROM series ORDER BY date_creation DESC')

def get_series_by_id(series_id):
    return db.fetch_one('SELECT * FROM series WHERE id = ?', (series_id,))

def add_quiz_to_series(series_id, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, ordre=0):
    db.query('INSERT INTO quiz (series_id, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, ordre) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (series_id, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, ordre))

def get_quiz_by_series(series_id):
    return db.fetch_all('SELECT * FROM quiz WHERE series_id = ? ORDER BY ordre', (series_id,))

def delete_quiz(quiz_id):
    db.query('DELETE FROM quiz WHERE id = ?', (quiz_id,))

def get_user_series_results(user_id):
    return db.fetch_all('SELECT * FROM resultats WHERE utilisateur_id = ? ORDER BY date_completion DESC', (user_id,))

def save_series_result(user_id, series_id, score, total):
    pourcentage = (score / total * 100) if total > 0 else 0
    db.query('INSERT INTO resultats (utilisateur_id, series_id, score, total, pourcentage) VALUES (?, ?, ?, ?, ?)',
            (user_id, series_id, score, total, pourcentage))

def toggle_user_status(user_id):
    user = db.fetch_one('SELECT status FROM utilisateurs WHERE id = ?', (user_id,))
    new_status = 'bloqué' if user['status'] == 'actif' else 'actif'
    db.query('UPDATE utilisateurs SET status = ? WHERE id = ?', (new_status, user_id))

def get_all_users():
    return db.fetch_all('SELECT * FROM utilisateurs WHERE role = "apprenant" ORDER BY date_creation DESC')

def add_feedback(email, titre, message, type_feedback):
    db.query('INSERT INTO feedback (email, titre, message, type, date_creation) VALUES (?, ?, ?, ?, ?)',
            (email, titre, message, type_feedback, datetime.now().isoformat()))

def get_all_feedback():
    return db.fetch_all('SELECT * FROM feedback ORDER BY date_creation DESC')

# ========== CSS PERSONNALISÉ ==========
st.markdown("""
<style>
    * { font-family: 'Segoe UI', sans-serif; }
    
    body {
        background-image: url('file:///mnt/user-data/outputs/logo_campus_reussite.jpg');
        background-size: cover;
        background-attachment: fixed;
    }
    
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    }
    
    .header-title {
        background: linear-gradient(135deg, #1a5f3d 0%, #d4a574 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(26, 95, 61, 0.3);
        text-align: center;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #1a5f3d 0%, #d4a574 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stat-number { font-size: 2.5rem; font-weight: 700; }
    .stat-label { font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem; }
    
    .series-card {
        background: white;
        border: 2px solid #1a5f3d;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .quiz-container {
        background: #f9f9f9;
        border-left: 4px solid #1a5f3d;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .admin-toggle {
        background: #f0f0f0;
        padding: 0.5rem;
        border-radius: 8px;
        cursor: pointer;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "accueil"
if "admin_tab" not in st.session_state:
    st.session_state.admin_tab = "dashboard"
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# ========== PAGE D'AUTHENTIFICATION ==========
if not st.session_state.logged_in:
    # Sidebar avec sélecteur caché pour admin
    with st.sidebar:
        st.markdown("### 🔐 Admin Panel")
        if st.button("🔧 Accès Admin (Secret)"):
            st.session_state.is_admin = True
            st.session_state.auth_mode = "admin_login"
            st.rerun()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="header-title" style="margin-bottom: 3rem;">
            <h1 style="font-size: 2.5rem; margin: 0;">🎓 Campus Réussite</h1>
            <p style="margin: 1rem 0 0; font-size: 1.1rem;">Plateforme d'Apprentissage Interactive</p>
        </div>
        """, unsafe_allow_html=True)
        
        # CONNEXION APPRENANT
        if st.session_state.auth_mode == "login":
            st.markdown("### Connexion Apprenant")
            
            email = st.text_input("Email", key="login_email")
            pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Se Connecter", use_container_width=True, type="primary"):
                    user = get_user_by_email(email)
                    if user and user['password'] == pwd:
                        if user['status'] == 'bloqué':
                            st.error("❌ Votre compte a été bloqué")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.session_state.is_admin = False
                            st.rerun()
                    else:
                        st.error("❌ Email ou mot de passe incorrect")
            
            with col2:
                if st.button("S'Inscrire", use_container_width=True):
                    st.session_state.auth_mode = "signup"
                    st.rerun()
        
        # INSCRIPTION APPRENANT
        elif st.session_state.auth_mode == "signup":
            st.markdown("### Créer un Compte")
            
            if st.button("← Retour", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()
            
            st.divider()
            
            nom = st.text_input("Nom", key="signup_nom")
            prenom = st.text_input("Prénom", key="signup_prenom")
            email = st.text_input("Email", key="signup_email")
            username = st.text_input("Username", key="signup_username")
            password = st.text_input("Mot de passe", type="password", key="signup_pwd")
            pwd_confirm = st.text_input("Confirmer", type="password", key="signup_pwd_confirm")
            
            if st.button("S'Inscrire", use_container_width=True, type="primary"):
                if not all([nom, prenom, email, username, password]):
                    st.error("❌ Remplissez tous les champs")
                elif not is_valid_email(email):
                    st.error("❌ Email invalide")
                elif len(password) < 6:
                    st.error("❌ Min 6 caractères")
                elif password != pwd_confirm:
                    st.error("❌ Mots de passe différents")
                elif get_user_by_email(email):
                    st.error("❌ Email déjà utilisé")
                elif add_user(nom, prenom, email, username, password):
                    st.success("✅ Compte créé!")
                    user = get_user_by_email(email)
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.is_admin = False
                    st.rerun()
                else:
                    st.error("❌ Erreur")
        
        # CONNEXION ADMIN
        elif st.session_state.auth_mode == "admin_login":
            st.markdown("### 🔐 Connexion Admin")
            
            if st.button("← Retour", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.session_state.is_admin = False
                st.rerun()
            
            st.divider()
            
            email = st.text_input("Email Admin", key="admin_login_email")
            pwd = st.text_input("Mot de passe", type="password", key="admin_login_pwd")
            
            TEST_ADMINS = {
                "admin@campus.fr": "12345678",
                "test@admin.com": "password123"
            }
            
            if st.button("Se Connecter", use_container_width=True, type="primary"):
                try:
                    admins = st.secrets.get("admins", {})
                    if email in admins and admins[email] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.user = {'nom': 'Admin', 'prenom': 'Campus', 'email': email, 'role': 'admin'}
                        st.session_state.is_admin = True
                        st.rerun()
                except:
                    pass
                
                if email in TEST_ADMINS and TEST_ADMINS[email] == pwd:
                    st.session_state.logged_in = True
                    st.session_state.user = {'nom': 'Admin', 'prenom': 'Campus', 'email': email, 'role': 'admin'}
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
                    st.info("💡 Test: admin@campus.fr / 12345678")

# ========== APPLICATION PRINCIPALE ==========
else:
    user = st.session_state.user
    
    # SIDEBAR
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"👤 **{user['prenom']} {user['nom']}**")
        st.markdown(f"📧 {user['email']}")
        
        if st.session_state.is_admin:
            st.markdown("---")
            st.markdown("### 🎛️ Admin Panel")
            if st.button("👨‍🎓 Mode Apprenant"):
                st.session_state.is_admin = False
                st.session_state.current_page = "accueil"
                st.rerun()
        else:
            st.markdown("---")
            # Sélecteur caché pour devenir admin (triple clic)
            st.markdown('<div class="admin-toggle">🔒</div>', unsafe_allow_html=True)
            if st.button("🔐 Admin (Secret)"):
                st.session_state.is_admin = True
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Déconnexion"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.is_admin = False
            st.rerun()
    
    # ========== MODE APPRENANT ==========
    if not st.session_state.is_admin:
        st.markdown("""
        <div class="header-title">
            <h1>🎓 Campus Réussite</h1>
            <p>Bienvenue, {0} {1}!</p>
        </div>
        """.format(user['prenom'], user['nom']), unsafe_allow_html=True)
        
        # Navigation
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🏠 Accueil", use_container_width=True):
                st.session_state.current_page = "accueil"
                st.rerun()
        with col2:
            if st.button("📚 Mes Séries", use_container_width=True):
                st.session_state.current_page = "series"
                st.rerun()
        with col3:
            if st.button("📊 Résultats", use_container_width=True):
                st.session_state.current_page = "resultats"
                st.rerun()
        with col4:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.current_page = "feedback"
                st.rerun()
        
        st.divider()
        
        # PAGE ACCUEIL
        if st.session_state.current_page == "accueil":
            col1, col2, col3 = st.columns(3)
            
            all_series = get_all_series()
            user_results = get_user_series_results(user['id'])
            completed_count = len(user_results)
            
            with col1:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(all_series)}</div><div class="stat-label">Séries Disponibles</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{completed_count}</div><div class="stat-label">Séries Complétées</div></div>', unsafe_allow_html=True)
            with col3:
                pct = (completed_count / len(all_series) * 100) if all_series else 0
                st.markdown(f'<div class="stat-box"><div class="stat-number">{pct:.0f}%</div><div class="stat-label">Progression</div></div>', unsafe_allow_html=True)
            
            st.divider()
            st.markdown("### 🎯 Commencer une Série")
            
            if all_series:
                for series in all_series:
                    result = next((r for r in user_results if r['series_id'] == series['id']), None)
                    status = f"✅ Score: {result['score']}/{result['total']}" if result else "⏳ À faire"
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{series['nom']}**")
                        st.markdown(f"{series['description']} | {series['nombre_questions']} questions | {status}")
                    with col2:
                        if st.button("Commencer" if not result else "Recommencer", key=f"series_{series['id']}", use_container_width=True):
                            st.session_state.current_page = f"series_{series['id']}"
                            st.rerun()
            else:
                st.info("📋 Aucune série disponible pour le moment")
        
        # PAGE SÉRIES
        elif st.session_state.current_page == "series":
            all_series = get_all_series()
            user_results = get_user_series_results(user['id'])
            
            st.markdown("### 📚 Mes Séries")
            
            if all_series:
                for series in all_series:
                    result = next((r for r in user_results if r['series_id'] == series['id']), None)
                    
                    st.markdown(f"""
                    <div class="series-card">
                        <h3>{series['nom']}</h3>
                        <p>{series['description']}</p>
                        <p>📝 {series['nombre_questions']} questions</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if result:
                        st.success(f"✅ Score: {result['score']}/{result['total']} ({result['pourcentage']:.1f}%)")
                    
                    if st.button("Faire la série" if not result else "Refaire", key=f"btn_series_{series['id']}", use_container_width=True):
                        st.session_state.current_page = f"series_{series['id']}"
                        st.rerun()
                    
                    st.divider()
            else:
                st.info("Aucune série")
        
        # PAGE RÉSULTATS
        elif st.session_state.current_page == "resultats":
            st.markdown("### 📊 Mes Résultats")
            
            user_results = get_user_series_results(user['id'])
            
            if user_results:
                df = pd.DataFrame([{
                    'Série': db.fetch_one('SELECT nom FROM series WHERE id = ?', (r['series_id'],))['nom'],
                    'Score': f"{r['score']}/{r['total']}",
                    'Pourcentage': f"{r['pourcentage']:.1f}%",
                    'Date': r['date_completion'][:10]
                } for r in user_results])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun résultat pour le moment")
        
        # PAGE FEEDBACK
        elif st.session_state.current_page == "feedback":
            st.markdown("### 💬 Envoyer un Feedback")
            
            with st.form("feedback_form"):
                titre = st.text_input("Titre")
                msg_type = st.selectbox("Type", ["Suggestion", "Problème", "Autre"])
                message = st.text_area("Message", height=150)
                
                if st.form_submit_button("Envoyer", use_container_width=True):
                    if titre and message:
                        add_feedback(user['email'], titre, message, msg_type)
                        st.success("✅ Feedback enregistré!")
                    else:
                        st.error("❌ Remplissez tous les champs")
        
        # PAGE QUIZ SÉRIE
        elif st.session_state.current_page.startswith("series_"):
            series_id = int(st.session_state.current_page.split("_")[1])
            series = get_series_by_id(series_id)
            quiz_list = get_quiz_by_series(series_id)
            
            st.markdown(f"### 🎯 {series['nom']}")
            st.markdown(f"{series['description']}")
            st.divider()
            
            st.markdown(f"**{len(quiz_list)} questions à répondre. Répondez à TOUTES avant de valider.**")
            
            # Initialiser les réponses
            if f"answers_{series_id}" not in st.session_state:
                st.session_state[f"answers_{series_id}"] = {}
            
            # Afficher tous les quizzes
            for idx, quiz in enumerate(quiz_list):
                st.markdown(f"<div class='quiz-container'>", unsafe_allow_html=True)
                st.markdown(f"**Question {idx+1}/{len(quiz_list)}: {quiz['question']}**")
                
                options = [quiz['option_a'], quiz['option_b'], quiz['option_c'], quiz['option_d']]
                
                selected = st.multiselect(
                    "Vos réponses:",
                    options,
                    default=st.session_state[f"answers_{series_id}"].get(quiz['id'], []),
                    key=f"quiz_{quiz['id']}"
                )
                
                st.session_state[f"answers_{series_id}"][quiz['id']] = selected
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.divider()
            
            # Bouton VALIDER (tout d'un coup)
            if st.button("✅ VALIDER LA SÉRIE", use_container_width=True, type="primary"):
                # Vérifier que toutes les questions sont répondues
                if len(st.session_state[f"answers_{series_id}"]) < len(quiz_list):
                    st.error("❌ Vous devez répondre à TOUTES les questions!")
                else:
                    # Calculer le score
                    score = 0
                    for quiz in quiz_list:
                        correct_answers = [c.strip() for c in quiz['reponses_correctes'].split(',')]
                        if set(st.session_state[f"answers_{series_id}"][quiz['id']]) == set(correct_answers):
                            score += 1
                    
                    # Sauvegarder le résultat
                    save_series_result(user['id'], series_id, score, len(quiz_list))
                    
                    # Afficher le score et les corrections
                    st.success(f"✅ SÉRIE COMPLÉTÉE!")
                    st.markdown(f"### 📊 Votre Score: {score}/{len(quiz_list)} ({score/len(quiz_list)*100:.1f}%)")
                    
                    st.divider()
                    st.markdown("### 📝 Corrections")
                    
                    for idx, quiz in enumerate(quiz_list):
                        correct_answers = [c.strip() for c in quiz['reponses_correctes'].split(',')]
                        your_answers = st.session_state[f"answers_{series_id}"][quiz['id']]
                        is_correct = set(your_answers) == set(correct_answers)
                        
                        with st.expander(f"Question {idx+1}: {quiz['question']}"):
                            st.markdown(f"**Votre réponse:** {', '.join(your_answers)}")
                            st.markdown(f"**Réponse correcte:** {', '.join(correct_answers)}")
                            if is_correct:
                                st.success("✅ Correct!")
                            else:
                                st.error("❌ Incorrect")
                            st.markdown(f"💡 **Explication:** {quiz['explication']}")
                    
                    st.divider()
                    if st.button("🏠 Retour à l'Accueil"):
                        st.session_state.current_page = "accueil"
                        del st.session_state[f"answers_{series_id}"]
                        st.rerun()
    
    # ========== MODE ADMIN ==========
    else:
        st.markdown("""
        <div class="header-title">
            <h1>🎛️ Dashboard Admin</h1>
            <p>Bienvenue, Administrateur!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.admin_tab = "dashboard"
                st.rerun()
        with col2:
            if st.button("📚 Séries", use_container_width=True):
                st.session_state.admin_tab = "series"
                st.rerun()
        with col3:
            if st.button("📤 Importer", use_container_width=True):
                st.session_state.admin_tab = "import"
                st.rerun()
        with col4:
            if st.button("👥 Apprenants", use_container_width=True):
                st.session_state.admin_tab = "users"
                st.rerun()
        with col5:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.admin_tab = "feedback"
                st.rerun()
        with col6:
            if st.button("🔍 DEBUG", use_container_width=True):
                st.session_state.admin_tab = "debug"
                st.rerun()
        
        st.divider()
        
        # DASHBOARD
        if st.session_state.admin_tab == "dashboard":
            st.markdown("### 📊 Statistiques")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(get_all_users())}</div><div class="stat-label">Apprenants</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(get_all_series())}</div><div class="stat-label">Séries</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(get_all_feedback())}</div><div class="stat-label">Feedbacks</div></div>', unsafe_allow_html=True)
            with col4:
                total_quiz = sum(len(get_quiz_by_series(s['id'])) for s in get_all_series())
                st.markdown(f'<div class="stat-box"><div class="stat-number">{total_quiz}</div><div class="stat-label">Quizzes</div></div>', unsafe_allow_html=True)
        
        # SÉRIES
        elif st.session_state.admin_tab == "series":
            st.markdown("### 📚 Gestion des Séries")
            
            # Ajouter une série
            with st.expander("➕ Créer une Nouvelle Série"):
                nom = st.text_input("Nom de la série")
                description = st.text_area("Description")
                nombre_q = st.slider("Nombre de questions", 1, 100, 50)
                
                if st.button("Créer la série", use_container_width=True):
                    if nom:
                        if add_series(nom, description, nombre_q):
                            st.success(f"✅ Série '{nom}' créée!")
                            st.rerun()
                        else:
                            st.error("❌ Erreur")
                    else:
                        st.error("❌ Nom requis")
            
            st.divider()
            
            # Ajouter quiz manuellement
            st.markdown("### ➕ Ajouter un Quiz Manuellement")
            
            series_list = get_all_series()
            if series_list:
                selected_series = st.selectbox("Choisir une série", [(s['id'], s['nom']) for s in series_list], format_func=lambda x: x[1])
                
                with st.form("add_quiz_form"):
                    question = st.text_input("Question")
                    opt_a = st.text_input("Option A")
                    opt_b = st.text_input("Option B")
                    opt_c = st.text_input("Option C")
                    opt_d = st.text_input("Option D")
                    correct = st.multiselect("Réponses correctes", ["A", "B", "C", "D"])
                    explication = st.text_area("Explication")
                    
                    if st.form_submit_button("Ajouter", use_container_width=True):
                        if all([question, opt_a, opt_b, opt_c, opt_d, correct, explication]):
                            correct_str = ", ".join(correct)
                            add_quiz_to_series(selected_series[0], question, opt_a, opt_b, opt_c, opt_d, correct_str, explication)
                            st.success("✅ Quiz ajouté!")
                            st.rerun()
                        else:
                            st.error("❌ Remplissez tous les champs")
            
            st.divider()
            
            # Lister les séries avec leurs quizzes
            st.markdown("### 📋 Séries Existantes")
            
            for series in series_list:
                quiz_count = len(get_quiz_by_series(series['id']))
                st.markdown(f"**{series['nom']}** ({quiz_count} quizzes)")
                st.markdown(f"_{series['description']}_")
                
                quiz_list = get_quiz_by_series(series['id'])
                if quiz_list:
                    for quiz in quiz_list:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"- {quiz['question']}")
                        with col2:
                            if st.button("🗑️", key=f"del_quiz_{quiz['id']}", help="Supprimer"):
                                delete_quiz(quiz['id'])
                                st.success("✅ Quiz supprimé")
                                st.rerun()
                
                st.divider()
        
        # IMPORTER
        elif st.session_state.admin_tab == "import":
            st.markdown("### 📤 Importer des Quiz")
            
            uploaded_file = st.file_uploader("Fichier CSV", type=["csv"])
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
                    st.success(f"✅ {len(df)} lignes chargées")
                    st.dataframe(df, use_container_width=True, height=300)
                    
                    series_list = get_all_series()
                    if series_list:
                        selected_series = st.selectbox("Ajouter à quelle série?", [(s['id'], s['nom']) for s in series_list], format_func=lambda x: x[1])
                        
                        if st.button("Ajouter à la série", use_container_width=True, type="primary"):
                            count = 0
                            for _, row in df.iterrows():
                                add_quiz_to_series(selected_series[0], row['question'], row['a'], row['b'], row['c'], row['d'],
                                                 row['reponses_correctes'], row['explication'])
                                count += 1
                            st.success(f"✅ {count} quizzes ajoutés!")
                            st.rerun()
                    else:
                        st.warning("⚠️ Créez d'abord une série")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
        
        # APPRENANTS
        elif st.session_state.admin_tab == "users":
            st.markdown("### 👥 Gestion des Apprenants")
            
            users = get_all_users()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(users)}</div><div class="stat-label">Total</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len([u for u in users if u["status"] == "actif"])}</div><div class="stat-label">Actifs</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len([u for u in users if u["status"] == "bloqué"])}</div><div class="stat-label">Bloqués</div></div>', unsafe_allow_html=True)
            
            st.divider()
            
            if users:
                for user_item in users:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        status_icon = "✅" if user_item['status'] == "actif" else "🔒"
                        st.markdown(f"{status_icon} **{user_item['prenom']} {user_item['nom']}**")
                        st.markdown(f"📧 {user_item['email']} | 👤 {user_item['username']}")
                    
                    with col2:
                        if st.button("Bloquer" if user_item['status'] == 'actif' else "Débloquer", key=f"toggle_{user_item['id']}", use_container_width=True):
                            toggle_user_status(user_item['id'])
                            st.rerun()
                    
                    with col3:
                        if st.button("Supprimer", key=f"del_{user_item['id']}", use_container_width=True):
                            db.query('DELETE FROM utilisateurs WHERE id = ?', (user_item['id'],))
                            st.rerun()
                    
                    st.divider()
            else:
                st.info("Aucun apprenant")
        
        # FEEDBACK
        elif st.session_state.admin_tab == "feedback":
            st.markdown("### 💬 Feedback des Apprenants")
            
            feedback_list = get_all_feedback()
            st.write(f"**{len(feedback_list)} feedbacks**")
            
            if feedback_list:
                for fb in feedback_list:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{fb['titre']}**")
                        st.markdown(f"De: {fb['email']} | Type: {fb['type']}")
                        st.markdown(f"Message: {fb['message']}")
                    with col2:
                        st.caption(fb['date_creation'][:10])
                    st.divider()
            else:
                st.info("Aucun feedback")
        
        # DEBUG
        elif st.session_state.admin_tab == "debug":
            st.markdown("### 🔍 DEBUG")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Apprenants", len(get_all_users()))
            with col2:
                st.metric("Séries", len(get_all_series()))
            with col3:
                st.metric("Quizzes", sum(len(get_quiz_by_series(s['id'])) for s in get_all_series()))
            with col4:
                st.metric("Feedbacks", len(get_all_feedback()))
