"""
🎓 CAMPUS RÉUSSITE v9.1 - COMPLÈTEMENT REDESSINÉ
✨ Interface Magnifique et Professionnelle
✅ Secrets pour Admin Principal + Admins en BD
✅ 100% Français
✅ Design Modern et Attractif
✅ UX Apprenant Optimisée
✅ Toutes les fonctionnalités v9.0
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import hashlib
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="Campus Réussite v9.1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_PATH = "campus.db"

# ========== CSS PROFESSIONNEL ==========
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stApp {
        background: white;
    }
    
    /* Header Professionnel */
    .header-main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
    }
    
    .header-main h1 {
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-main p {
        font-size: 1.1em;
        opacity: 0.95;
    }
    
    /* Cards Moderne */
    .card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        transform: translateY(-5px);
    }
    
    .card-quiz {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin: 15px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .card-quiz:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    /* Stats */
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
    }
    
    .stat-number {
        font-size: 2.5em;
        margin: 10px 0;
    }
    
    /* Boutons */
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 30px;
        border-radius: 25px;
        border: none;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .btn-success {
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
        color: white;
        padding: 12px 30px;
        border-radius: 25px;
        border: none;
        cursor: pointer;
        font-weight: bold;
    }
    
    /* Questions Quiz */
    .question-box {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 5px solid #667eea;
    }
    
    .option-box {
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .option-box:hover {
        border-color: #667eea;
        background: #f0f4ff;
    }
    
    /* Résultats */
    .result-box {
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin: 20px 0;
    }
    
    .result-score {
        font-size: 3em;
        font-weight: bold;
        margin: 10px 0;
    }
    
    /* Navigation Tabs */
    .tabs-custom {
        display: flex;
        gap: 10px;
        margin: 20px 0;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .tab-item {
        padding: 15px 25px;
        cursor: pointer;
        border: none;
        background: white;
        border-bottom: 3px solid transparent;
        transition: all 0.3s ease;
    }
    
    .tab-item:hover {
        border-bottom-color: #667eea;
        color: #667eea;
    }
    
    .tab-item.active {
        border-bottom-color: #667eea;
        color: #667eea;
        font-weight: bold;
    }
    
    /* Info Messages */
    .info-box {
        background: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    
    .success-box {
        background: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    
    .error-box {
        background: #ffebee;
        border-left: 5px solid #f44336;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    
    /* Timeouts */
    .timeout-indicator {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-weight: bold;
        z-index: 1000;
    }
    
    .timeout-green {
        color: #10b981;
        border: 2px solid #10b981;
    }
    
    .timeout-orange {
        color: #f59e0b;
        border: 2px solid #f59e0b;
    }
    
    .timeout-red {
        color: #ef4444;
        border: 2px solid #ef4444;
    }
</style>
""", unsafe_allow_html=True)

# ========== DATABASE CLASS ==========
class DB:
    def __init__(self):
        self.init()
    
    def init(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Utilisateurs (apprenants)
        c.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY, 
            nom TEXT, 
            prenom TEXT, 
            email TEXT UNIQUE,
            password_hash TEXT, 
            role TEXT DEFAULT 'apprenant',
            status TEXT DEFAULT 'actif', 
            session_minutes INTEGER DEFAULT 120,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Admins (en base de données)
        c.execute('''CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY, 
            email TEXT UNIQUE,
            password_hash TEXT, 
            nom TEXT, 
            prenom TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'actif')''')
        
        # Séries
        c.execute('''CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY, 
            nom TEXT UNIQUE, 
            description TEXT, 
            nombre_questions INTEGER DEFAULT 0)''')
        
        # Quizzes
        c.execute('''CREATE TABLE IF NOT EXISTS quiz (
            id INTEGER PRIMARY KEY, 
            series_id INTEGER, 
            question TEXT, 
            option_a TEXT,
            option_b TEXT, 
            option_c TEXT, 
            option_d TEXT, 
            reponses_correctes TEXT, 
            explication TEXT)''')
        
        # Quizzes en attente
        c.execute('''CREATE TABLE IF NOT EXISTS quiz_pending (
            id INTEGER PRIMARY KEY, 
            question TEXT, 
            option_a TEXT, 
            option_b TEXT,
            option_c TEXT, 
            option_d TEXT, 
            reponses_correctes TEXT, 
            explication TEXT, 
            categorie TEXT)''')
        
        # Résultats
        c.execute('''CREATE TABLE IF NOT EXISTS resultats (
            id INTEGER PRIMARY KEY, 
            utilisateur_id INTEGER, 
            series_id INTEGER,
            score INTEGER, 
            total INTEGER, 
            pourcentage REAL,
            date_test TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Feedback
        c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY, 
            email TEXT, 
            titre TEXT, 
            message TEXT, 
            type TEXT,
            date_feedback TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
    
    def q(self, sql, p=()):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(sql, p)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False
    
    def f1(self, sql, p=()):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            r = conn.execute(sql, p).fetchone()
            conn.close()
            return dict(r) if r else None
        except:
            return None
    
    def fa(self, sql, p=()):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            r = conn.execute(sql, p).fetchall()
            conn.close()
            return [dict(x) for x in r] if r else []
        except:
            return []

db = DB()

def hash_pwd(p):
    return hashlib.sha256((p + "salt2024").encode()).hexdigest()

def verify_pwd(p, h):
    return hash_pwd(p) == h

# ========== SESSION MANAGEMENT ==========
def check_session_timeout():
    if st.session_state.logged_in and st.session_state.user and not st.session_state.is_admin:
        user = db.f1('SELECT * FROM utilisateurs WHERE id=?', (st.session_state.user['id'],))
        if user:
            last_activity = datetime.fromisoformat(user['last_activity'])
            timeout_minutes = user['session_minutes']
            elapsed = (datetime.now() - last_activity).total_seconds() / 60
            
            if elapsed > timeout_minutes:
                st.session_state.logged_in = False
                st.session_state.user = None
                st.warning("⏰ Session expirée!")
                st.rerun()

def update_activity():
    if st.session_state.logged_in and st.session_state.user and not st.session_state.is_admin:
        db.q('UPDATE utilisateurs SET last_activity=? WHERE id=?',
            (datetime.now(), st.session_state.user['id']))

# ========== EXPORT/IMPORT ==========
def export_database():
    try:
        export_data = {
            'utilisateurs': db.fa('SELECT * FROM utilisateurs'),
            'admins': db.fa('SELECT * FROM admins'),
            'series': db.fa('SELECT * FROM series'),
            'quiz': db.fa('SELECT * FROM quiz'),
            'resultats': db.fa('SELECT * FROM resultats'),
            'feedback': db.fa('SELECT * FROM feedback'),
            'export_date': datetime.now().isoformat(),
            'version': '9.1'
        }
        return json.dumps(export_data, indent=2, default=str)
    except Exception as e:
        return None

def import_database(json_data):
    try:
        data = json.loads(json_data)
        db.init()
        
        for user in data.get('utilisateurs', []):
            db.q('INSERT INTO utilisateurs (nom,prenom,email,password_hash,role,status,session_minutes,last_activity) VALUES (?,?,?,?,?,?,?,?)',
                (user.get('nom'), user.get('prenom'), user.get('email'),
                 user.get('password_hash'), user.get('role'), user.get('status'), 
                 user.get('session_minutes', 120), user.get('last_activity')))
        
        for admin in data.get('admins', []):
            db.q('INSERT INTO admins (email,password_hash,nom,prenom,date_creation,status) VALUES (?,?,?,?,?,?)',
                (admin.get('email'), admin.get('password_hash'), admin.get('nom'),
                 admin.get('prenom'), admin.get('date_creation'), admin.get('status', 'actif')))
        
        for serie in data.get('series', []):
            db.q('INSERT INTO series (nom,description,nombre_questions) VALUES (?,?,?)',
                (serie.get('nom'), serie.get('description'), serie.get('nombre_questions', 0)))
        
        for quiz in data.get('quiz', []):
            db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)',
                (quiz.get('series_id'), quiz.get('question'), quiz.get('option_a'),
                 quiz.get('option_b'), quiz.get('option_c'), quiz.get('option_d'),
                 quiz.get('reponses_correctes'), quiz.get('explication')))
        
        for res in data.get('resultats', []):
            db.q('INSERT INTO resultats (utilisateur_id,series_id,score,total,pourcentage,date_test) VALUES (?,?,?,?,?,?)',
                (res.get('utilisateur_id'), res.get('series_id'), res.get('score'),
                 res.get('total'), res.get('pourcentage'), res.get('date_test')))
        
        for fb in data.get('feedback', []):
            db.q('INSERT INTO feedback (email,titre,message,type,date_feedback) VALUES (?,?,?,?,?)',
                (fb.get('email'), fb.get('titre'), fb.get('message'),
                 fb.get('type'), fb.get('date_feedback')))
        
        return True
    except Exception as e:
        return False

# ========== INIT SESSION STATE ==========
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "admin_tab" not in st.session_state:
    st.session_state.admin_tab = "dash"
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "editing_quiz_id" not in st.session_state:
    st.session_state.editing_quiz_id = None
if "current_series_id" not in st.session_state:
    st.session_state.current_series_id = None

check_session_timeout()
update_activity()

# ========== LOGIN PAGE ==========
if not st.session_state.logged_in:
    st.markdown("""
    <div class="header-main">
        <h1>🎓 Campus Réussite</h1>
        <p>Plateforme d'apprentissage interactive et performante</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with tab1:
            st.subheader("🔐 Connexion à votre compte")
            email = st.text_input("📧 Adresse email")
            pwd = st.text_input("🔑 Mot de passe", type="password")
            
            if st.button("✨ Se Connecter", use_container_width=True, type="primary"):
                # Vérifier Admin Principal via Secrets
                try:
                    admins_secrets = st.secrets.get("admins", {})
                    if email.lower() in admins_secrets and admins_secrets[email.lower()] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.session_state.user = {'nom':'Principal','prenom':'Admin','email':email.lower(),'id':0}
                        st.success("✅ Connexion Admin réussie!")
                        st.rerun()
                except:
                    pass
                
                # Vérifier Admins en BD
                admin = db.f1('SELECT * FROM admins WHERE email=? AND status="actif"', (email.lower(),))
                if admin and verify_pwd(pwd, admin['password_hash']):
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.user = admin
                    st.success("✅ Connexion Admin réussie!")
                    st.rerun()
                
                # Vérifier Apprenant
                user = db.f1('SELECT * FROM utilisateurs WHERE email=?', (email.lower(),))
                if user and verify_pwd(pwd, user['password_hash']):
                    if user['status'] == 'bloqué':
                        st.error("❌ Votre compte a été bloqué")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.is_admin = False
                        st.success("✅ Bienvenue!")
                        st.rerun()
                else:
                    st.error("❌ Email ou mot de passe incorrect")
        
        with tab2:
            st.subheader("📝 Créer un nouveau compte")
            col_nom, col_prenom = st.columns(2)
            with col_nom:
                nom = st.text_input("👤 Nom")
            with col_prenom:
                prenom = st.text_input("👤 Prénom")
            
            email = st.text_input("📧 Adresse email", key="reg_email")
            password = st.text_input("🔑 Mot de passe (min 6 caractères)", type="password", key="reg_pwd")
            pwd_confirm = st.text_input("🔑 Confirmer le mot de passe", type="password", key="reg_confirm")
            
            st.info("💡 Utilisez votre email pour vous connecter par la suite")
            
            if st.button("✨ S'inscrire", use_container_width=True, type="primary"):
                if len(password) < 6:
                    st.error("❌ Mot de passe trop court (minimum 6 caractères)")
                elif password != pwd_confirm:
                    st.error("❌ Les mots de passe ne correspondent pas")
                elif not nom or not prenom or not email:
                    st.error("❌ Remplissez tous les champs")
                else:
                    result = db.q('INSERT INTO utilisateurs (nom,prenom,email,password_hash) VALUES (?,?,?,?)',
                        (nom, prenom, email.lower(), hash_pwd(password)))
                    if result:
                        st.success("✅ Compte créé avec succès! Connectez-vous maintenant.")
                    else:
                        st.error("❌ Cet email est déjà utilisé")

# ========== APPRENANT INTERFACE ==========
elif st.session_state.logged_in and not st.session_state.is_admin:
    # Header
    st.markdown(f"""
    <div class="header-main">
        <h1>👋 Bienvenue {st.session_state.user['prenom']}!</h1>
        <p>Continuez votre apprentissage et progressez</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Timeout indicator
    user = db.f1('SELECT * FROM utilisateurs WHERE id=?', (st.session_state.user['id'],))
    if user:
        last_activity = datetime.fromisoformat(user['last_activity'])
        elapsed = int((datetime.now() - last_activity).total_seconds() / 60)
        timeout = user['session_minutes']
        remaining = max(0, timeout - elapsed)
        
        if remaining > 10:
            timeout_class = "timeout-green"
        elif remaining > 0:
            timeout_class = "timeout-orange"
        else:
            timeout_class = "timeout-red"
        
        st.markdown(f"""
        <div class="timeout-indicator {timeout_class}">
            ⏱️ {remaining}/{timeout} min restantes
        </div>
        """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📚 Commencer un quiz", "📊 Mes résultats", "📝 Envoyer un feedback"])
    
    # ========== TAB 1: QUIZZES ==========
    with tab1:
        series = db.fa('SELECT * FROM series')
        
        if series:
            st.subheader("Choisissez une série pour commencer")
            st.write("---")
            
            cols = st.columns(2)
            for idx, s in enumerate(series):
                quizzes = db.fa('SELECT * FROM quiz WHERE series_id=?', (s['id'],))
                
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="card-quiz">
                        <div style="font-size: 2em; margin-bottom: 10px;">📚</div>
                        <h3 style="color: white; margin-bottom: 10px;">{s['nom']}</h3>
                        <p style="color: rgba(255,255,255,0.9); margin-bottom: 15px;">{s['description']}</p>
                        <div style="font-size: 1.3em; color: rgba(255,255,255,0.95); font-weight: bold;">
                            🎯 {len(quizzes)} questions
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Commencer {s['nom']}", key=f"quiz_{s['id']}", use_container_width=True):
                        st.session_state.page = f"quiz_{s['id']}"
                        st.session_state.current_series_id = s['id']
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.rerun()
        else:
            st.info("ℹ️ Aucun quiz disponible pour le moment. Revenez bientôt!")
        
        # Quiz Display
        for s in series:
            if st.session_state.page == f"quiz_{s['id']}":
                st.markdown(f"""
                <div class="header-main" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-align: center;">
                    <h2>📖 {s['nom']}</h2>
                    <p>{s['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                quizzes = db.fa('SELECT * FROM quiz WHERE series_id=?', (s['id'],))
                
                if quizzes:
                    # Progress
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        progress = len(st.session_state.quiz_answers) / len(quizzes)
                        st.metric("Progression", f"{int(progress*100)}%")
                    
                    st.write("---")
                    
                    # Questions
                    for idx, q in enumerate(quizzes, 1):
                        st.markdown(f"""
                        <div class="question-box">
                            <h4>Question {idx}/{len(quizzes)}</h4>
                            <h3 style="color: #667eea; margin-top: 10px;">{q['question']}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Options
                        options = ["A", "B", "C", "D"]
                        option_texts = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
                        
                        selected = st.radio(
                            "Sélectionnez votre réponse:",
                            options,
                            format_func=lambda x: f"{x}) {option_texts[ord(x)-65]}",
                            key=f"q_{q['id']}",
                            label_visibility="collapsed"
                        )
                        
                        st.session_state.quiz_answers[q['id']] = selected
                        st.write("")
                    
                    st.write("---")
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("⬅️ Retour", use_container_width=True):
                            st.session_state.page = "home"
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_submitted = False
                            st.rerun()
                    
                    with col2:
                        if st.button("✅ Soumettre les réponses", use_container_width=True, type="primary"):
                            score = 0
                            for q in quizzes:
                                if q['id'] in st.session_state.quiz_answers:
                                    if st.session_state.quiz_answers[q['id']] in q['reponses_correctes'].split(","):
                                        score += 1
                            
                            percentage = (score / len(quizzes)) * 100
                            db.q('INSERT INTO resultats (utilisateur_id,series_id,score,total,pourcentage) VALUES (?,?,?,?,?)',
                                (st.session_state.user['id'], s['id'], score, len(quizzes), percentage))
                            
                            st.session_state.quiz_submitted = True
                            st.session_state.page = f"results_{s['id']}"
                            st.rerun()
                
                # Results Page
                if st.session_state.page == f"results_{s['id']}" and st.session_state.quiz_submitted:
                    resultat = db.f1(
                        'SELECT * FROM resultats WHERE utilisateur_id=? AND series_id=? ORDER BY id DESC LIMIT 1',
                        (st.session_state.user['id'], s['id'])
                    )
                    
                    if resultat:
                        percentage = resultat['pourcentage']
                        color = "green" if percentage >= 60 else "orange" if percentage >= 40 else "red"
                        
                        st.markdown(f"""
                        <div class="result-box" style="background: linear-gradient(135deg, {'#34d399' if percentage >= 60 else '#f59e0b' if percentage >= 40 else '#ef4444'} 0%, {'#10b981' if percentage >= 60 else '#d97706' if percentage >= 40 else '#dc2626'} 100%);">
                            <h2>✨ Quiz Complété!</h2>
                            <div class="result-score">{resultat['score']}/{resultat['total']}</div>
                            <p style="font-size: 1.3em;">{percentage:.1f}%</p>
                            <p style="margin-top: 10px; font-size: 1em;">
                                {'🎉 Excellent travail!' if percentage >= 80 else '👍 Bon travail!' if percentage >= 60 else '💪 Continuez vos efforts!'}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.write("---")
                        
                        # Détails réponses
                        if st.checkbox("Voir le détail des réponses"):
                            for q in quizzes:
                                user_answer = st.session_state.quiz_answers.get(q['id'], 'Non répondu')
                                is_correct = user_answer in q['reponses_correctes'].split(",")
                                
                                st.markdown(f"""
                                <div style="padding: 15px; border-radius: 8px; margin: 10px 0; background: {'#e8f5e9' if is_correct else '#ffebee'}; border-left: 5px solid {'#4caf50' if is_correct else '#f44336'};">
                                    <strong>{'✅' if is_correct else '❌'} {q['question']}</strong><br>
                                    <small>Votre réponse: {user_answer}) {option_texts[ord(user_answer)-65] if user_answer != 'Non répondu' else 'Non répondu'}</small><br>
                                    <small>Correcte(s): {q['reponses_correctes']}</small><br>
                                    <small><em>Explication: {q['explication']}</em></small>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔄 Recommencer ce quiz", use_container_width=True):
                                st.session_state.page = f"quiz_{s['id']}"
                                st.session_state.quiz_answers = {}
                                st.session_state.quiz_submitted = False
                                st.rerun()
                        
                        with col2:
                            if st.button("📚 Choisir une autre série", use_container_width=True):
                                st.session_state.page = "home"
                                st.session_state.quiz_answers = {}
                                st.session_state.quiz_submitted = False
                                st.rerun()
    
    # ========== TAB 2: RÉSULTATS ==========
    with tab2:
        st.subheader("📊 Votre historique de résultats")
        
        resultats = db.fa('SELECT * FROM resultats WHERE utilisateur_id=? ORDER BY date_test DESC', 
                          (st.session_state.user['id'],))
        
        if resultats:
            for res in resultats:
                serie = db.f1('SELECT * FROM series WHERE id=?', (res['series_id'],))
                
                # Color based on percentage
                if res['pourcentage'] >= 80:
                    emoji = "🎉"
                elif res['pourcentage'] >= 60:
                    emoji = "👍"
                else:
                    emoji = "💪"
                
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3>{emoji} {serie['nom']}</h3>
                            <p style="color: #666;">Résultat: <strong>{res['score']}/{res['total']}</strong></p>
                            <small>📅 {res['date_test']}</small>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 2em; font-weight: bold; color: #667eea;">{res['pourcentage']:.1f}%</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Vous n'avez pas encore de résultats. Commencez un quiz!")
    
    # ========== TAB 3: FEEDBACK ==========
    with tab3:
        st.subheader("📝 Nous aimerions avoir votre avis")
        
        titre = st.text_input("Titre du feedback")
        msg = st.text_area("Votre message")
        type_fb = st.selectbox("Type de feedback", 
            ["💡 Suggestion", "🐛 Problème/Bug", "👍 Compliment", "❓ Question", "📣 Autre"])
        
        if st.button("📤 Envoyer le feedback", use_container_width=True, type="primary"):
            if titre and msg:
                db.q('INSERT INTO feedback (email,titre,message,type) VALUES (?,?,?,?)',
                    (st.session_state.user['email'], titre, msg, type_fb))
                st.success("✅ Merci! Votre feedback a été envoyé.")
            else:
                st.error("❌ Remplissez tous les champs")
    
    # Logout
    st.write("---")
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# ========== ADMIN INTERFACE ==========
elif st.session_state.logged_in and st.session_state.is_admin:
    st.markdown("""
    <div class="header-main">
        <h1>🔐 Panneau d'Administration</h1>
        <p>Gestion complète de la plateforme</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Admin Menu
    admin_tabs = st.tabs([
        "📊 Dashboard",
        "📚 Séries",
        "🎯 Quizzes",
        "📤 Importer",
        "👥 Apprenants",
        "👨‍💼 Administrateurs",
        "💾 Base Données",
        "💬 Feedback"
    ])
    
    # ========== DASHBOARD ==========
    with admin_tabs[0]:
        st.subheader("📊 Statistiques Principales")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            users_count = len(db.fa('SELECT * FROM utilisateurs'))
            st.markdown(f'<div class="stat-box"><div style="font-size: 0.9em;">👥 Apprenants</div><div class="stat-number">{users_count}</div></div>', unsafe_allow_html=True)
        with col2:
            series_count = len(db.fa('SELECT * FROM series'))
            st.markdown(f'<div class="stat-box"><div style="font-size: 0.9em;">📚 Séries</div><div class="stat-number">{series_count}</div></div>', unsafe_allow_html=True)
        with col3:
            quizzes_count = len(db.fa('SELECT * FROM quiz'))
            st.markdown(f'<div class="stat-box"><div style="font-size: 0.9em;">🎯 Quizzes</div><div class="stat-number">{quizzes_count}</div></div>', unsafe_allow_html=True)
        with col4:
            feedback_count = len(db.fa('SELECT * FROM feedback'))
            st.markdown(f'<div class="stat-box"><div style="font-size: 0.9em;">💬 Feedbacks</div><div class="stat-number">{feedback_count}</div></div>', unsafe_allow_html=True)
    
    # ========== SÉRIES ==========
    with admin_tabs[1]:
        st.subheader("📚 Gestion des Séries")
        
        with st.expander("➕ Créer une nouvelle série"):
            nom = st.text_input("Nom de la série")
            desc = st.text_area("Description")
            if st.button("Créer la série", use_container_width=True, type="primary"):
                if nom:
                    if db.q('INSERT INTO series (nom,description) VALUES (?,?)', (nom, desc)):
                        st.success("✅ Série créée avec succès!")
                        st.rerun()
                    else:
                        st.error("❌ Cette série existe déjà")
                else:
                    st.error("❌ Entrez un nom")
        
        st.write("---")
        st.subheader("Séries existantes")
        
        series = db.fa('SELECT * FROM series')
        for s in series:
            quiz_count = len(db.fa('SELECT * FROM quiz WHERE series_id=?', (s['id'],)))
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="card">
                    <h3>{s['nom']}</h3>
                    <p style="color: #666;">{s['description']}</p>
                    <small style="color: #999;">🎯 {quiz_count} quizzes</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🗑️ Supprimer", key=f"del_serie_{s['id']}", use_container_width=True):
                    db.q('DELETE FROM quiz WHERE series_id=?', (s['id'],))
                    db.q('DELETE FROM series WHERE id=?', (s['id'],))
                    st.success("✅ Série supprimée")
                    st.rerun()
    
    # ========== QUIZZES (NOUVEAU DESIGN) ==========
    with admin_tabs[2]:
        st.subheader("🎯 Gestion des Quizzes")
        
        series = db.fa('SELECT * FROM series')
        if series:
            selected_series = st.selectbox(
                "Sélectionner une série",
                [(s['id'], s['nom']) for s in series],
                format_func=lambda x: x[1]
            )
            
            st.write("---")
            quizzes = db.fa('SELECT * FROM quiz WHERE series_id=?', (selected_series[0],))
            
            st.write(f"**{len(quizzes)} quizzes dans cette série**")
            
            for idx, q in enumerate(quizzes, 1):
                col1, col2, col3 = st.columns([3, 0.5, 0.5])
                
                with col1:
                    st.markdown(f"""
                    <div class="card">
                        <strong>Q{idx}: {q['question']}</strong>
                        <small style="display: block; margin-top: 10px; color: #666;">
                            A) {q['option_a']}<br>
                            B) {q['option_b']}<br>
                            C) {q['option_c']}<br>
                            D) {q['option_d']}<br>
                            <strong style="color: #667eea;">Réponse(s): {q['reponses_correctes']}</strong>
                        </small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("✏️", key=f"edit_{q['id']}", help="Éditer"):
                        st.session_state.editing_quiz_id = q['id']
                
                with col3:
                    if st.button("🗑️", key=f"del_quiz_{q['id']}", help="Supprimer"):
                        db.q('DELETE FROM quiz WHERE id=?', (q['id'],))
                        st.success("✅ Quiz supprimé")
                        st.rerun()
                
                # Formulaire édition
                if st.session_state.editing_quiz_id == q['id']:
                    st.write("---")
                    st.markdown("### ✏️ Éditer ce quiz")
                    
                    with st.form("edit_form"):
                        new_q = st.text_input("Question", value=q['question'])
                        new_a = st.text_input("Option A", value=q['option_a'])
                        new_b = st.text_input("Option B", value=q['option_b'])
                        new_c = st.text_input("Option C", value=q['option_c'])
                        new_d = st.text_input("Option D", value=q['option_d'])
                        new_correct = st.multiselect("Réponses correctes", ["A", "B", "C", "D"],
                            default=q['reponses_correctes'].split(","))
                        new_expl = st.text_area("Explication", value=q['explication'])
                        
                        if st.form_submit_button("💾 Sauvegarder"):
                            db.q('UPDATE quiz SET question=?,option_a=?,option_b=?,option_c=?,option_d=?,reponses_correctes=?,explication=? WHERE id=?',
                                (new_q, new_a, new_b, new_c, new_d, ",".join(new_correct), new_expl, q['id']))
                            st.success("✅ Quiz modifié")
                            st.session_state.editing_quiz_id = None
                            st.rerun()
        else:
            st.info("ℹ️ Créez d'abord une série!")
    
    # ========== IMPORT ==========
    with admin_tabs[3]:
        st.subheader("📤 Importer des Quizzes depuis CSV")
        
        uploaded_file = st.file_uploader("Sélectionnez un fichier CSV", type=["csv"])
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, sep=";")
                st.success(f"✅ {len(df)} quizzes chargés")
                
                st.write("**Aperçu - Vous pouvez éditer les données:**")
                edited_df = st.data_editor(df, use_container_width=True, height=400)
                
                series_list = db.fa('SELECT * FROM series')
                if series_list:
                    sel_series = st.selectbox(
                        "Ajouter à quelle série?",
                        [(s['id'], s['nom']) for s in series_list],
                        format_func=lambda x: x[1]
                    )
                    
                    if st.button("📥 Importer les quizzes", use_container_width=True, type="primary"):
                        count = 0
                        for _, row in edited_df.iterrows():
                            db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)',
                                (sel_series[0], row['question'], row['a'], row['b'], row['c'], row['d'],
                                 row['reponses_correctes'], row['explication']))
                            count += 1
                        st.success(f"✅ {count} quizzes importés!")
                        st.rerun()
                else:
                    st.error("❌ Créez une série d'abord!")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    # ========== APPRENANTS ==========
    with admin_tabs[4]:
        st.subheader("👥 Gestion des Apprenants")
        
        users = db.fa('SELECT * FROM utilisateurs')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-box"><div style="font-size: 0.9em;">Total</div><div class="stat-number">{len(users)}</div></div>', unsafe_allow_html=True)
        with col2:
            active = len([u for u in users if u['status'] == 'actif'])
            st.markdown(f'<div class="stat-box"><div style="font-size: 0.9em;">Actifs</div><div class="stat-number">{active}</div></div>', unsafe_allow_html=True)
        with col3:
            blocked = len([u for u in users if u['status'] == 'bloqué'])
            st.markdown(f'<div class="stat-box"><div style="font-size: 0.9em;">Bloqués</div><div class="stat-number">{blocked}</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        
        for u in users:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                icon = "✅" if u['status'] == 'actif' else "🔒"
                st.markdown(f"**{icon} {u['prenom']} {u['nom']}**")
                st.caption(f"📧 {u['email']}")
            
            with col2:
                if st.button("🔒 Bloquer" if u['status'] == 'actif' else "✅ Débloquer", 
                            key=f"block_{u['id']}", use_container_width=True):
                    new_status = 'bloqué' if u['status'] == 'actif' else 'actif'
                    db.q('UPDATE utilisateurs SET status=? WHERE id=?', (new_status, u['id']))
                    st.rerun()
            
            with col3:
                new_dur = st.number_input("Min", 5, 1440, u['session_minutes'], 
                                         key=f"dur_{u['id']}", step=1)
                if new_dur != u['session_minutes']:
                    db.q('UPDATE utilisateurs SET session_minutes=? WHERE id=?', (new_dur, u['id']))
                    st.rerun()
            
            with col4:
                if st.button("🗑️ Supprimer", key=f"del_{u['id']}", use_container_width=True):
                    db.q('DELETE FROM utilisateurs WHERE id=?', (u['id'],))
                    st.rerun()
            
            st.divider()
    
    # ========== ADMINISTRATEURS ==========
    with admin_tabs[5]:
        st.subheader("👨‍💼 Gestion des Administrateurs")
        
        with st.expander("➕ Créer un nouvel administrateur"):
            nom_admin = st.text_input("Nom")
            prenom_admin = st.text_input("Prénom")
            email_admin = st.text_input("Email")
            pwd_admin = st.text_input("Mot de passe (min 8 caractères)", type="password")
            pwd_admin_confirm = st.text_input("Confirmer le mot de passe", type="password")
            
            if st.button("Créer l'administrateur", use_container_width=True, type="primary"):
                if len(pwd_admin) < 8:
                    st.error("❌ Mot de passe trop court (minimum 8)")
                elif pwd_admin != pwd_admin_confirm:
                    st.error("❌ Les mots de passe ne correspondent pas")
                elif not all([nom_admin, prenom_admin, email_admin]):
                    st.error("❌ Remplissez tous les champs")
                else:
                    if db.q('INSERT INTO admins (email,password_hash,nom,prenom) VALUES (?,?,?,?)',
                        (email_admin.lower(), hash_pwd(pwd_admin), nom_admin, prenom_admin)):
                        st.success(f"✅ Admin créé: {email_admin}")
                        st.rerun()
                    else:
                        st.error("❌ Cet email est déjà utilisé")
        
        st.write("---")
        st.subheader("Administrateurs actuels")
        
        admins = db.fa('SELECT * FROM admins')
        for admin in admins:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                icon = "✅" if admin['status'] == 'actif' else "🔒"
                st.markdown(f"**{icon} {admin['prenom']} {admin['nom']}**")
                st.caption(f"📧 {admin['email']}")
            
            with col2:
                if st.button("🔒" if admin['status'] == 'actif' else "✅", 
                            key=f"admin_block_{admin['id']}", use_container_width=True):
                    new_status = 'bloqué' if admin['status'] == 'actif' else 'actif'
                    db.q('UPDATE admins SET status=? WHERE id=?', (new_status, admin['id']))
                    st.rerun()
            
            with col3:
                if st.button("🗑️", key=f"del_admin_{admin['id']}", use_container_width=True):
                    db.q('DELETE FROM admins WHERE id=?', (admin['id'],))
                    st.rerun()
            
            st.divider()
    
    # ========== BASE DE DONNÉES ==========
    with admin_tabs[6]:
        st.subheader("💾 Gestion de la Base de Données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📥 Exporter")
            if st.button("Télécharger sauvegarde complète", use_container_width=True, type="primary"):
                export_json = export_database()
                if export_json:
                    st.download_button(
                        label="💾 Télécharger JSON",
                        data=export_json,
                        file_name=f"campus_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        
        with col2:
            st.markdown("### 📤 Importer")
            backup_file = st.file_uploader("Uploader une sauvegarde JSON", type=["json"])
            if backup_file:
                try:
                    json_data = backup_file.read().decode("utf-8")
                    if st.button("🔄 Restaurer la sauvegarde", use_container_width=True, type="primary"):
                        if import_database(json_data):
                            st.success("✅ Base de données restaurée!")
                            st.rerun()
                        else:
                            st.error("❌ Erreur de restauration")
                except:
                    st.error("❌ Fichier invalide")
        
        st.write("---")
        st.subheader("📊 Informations")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Utilisateurs", len(db.fa('SELECT * FROM utilisateurs')))
        with col2:
            st.metric("Admins", len(db.fa('SELECT * FROM admins')))
        with col3:
            st.metric("Séries", len(db.fa('SELECT * FROM series')))
        with col4:
            st.metric("Quizzes", len(db.fa('SELECT * FROM quiz')))
        with col5:
            st.metric("Résultats", len(db.fa('SELECT * FROM resultats')))
        with col6:
            st.metric("Feedbacks", len(db.fa('SELECT * FROM feedback')))
    
    # ========== FEEDBACK ==========
    with admin_tabs[7]:
        st.subheader("💬 Feedbacks des Apprenants")
        
        feedbacks = db.fa('SELECT * FROM feedback ORDER BY date_feedback DESC')
        
        if feedbacks:
            for fb in feedbacks:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="card">
                        <strong>{fb['titre']}</strong> - {fb['type']}<br>
                        <small>📧 {fb['email']}</small><br>
                        <p style="margin-top: 10px;">{fb['message']}</p>
                        <small style="color: #999;">📅 {fb['date_feedback']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("🗑️", key=f"del_fb_{fb['id']}", use_container_width=True):
                        db.q('DELETE FROM feedback WHERE id=?', (fb['id'],))
                        st.rerun()
        else:
            st.info("ℹ️ Aucun feedback pour le moment")
    
    st.write("---")
    if st.button("🚪 Déconnexion Admin", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.is_admin = False
        st.rerun()
