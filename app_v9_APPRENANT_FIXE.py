"""
🎓 CAMPUS RÉUSSITE - PAGE APPRENANT FIXÉE
✅ Corrections s'affichent immédiatement après soumission
✅ Simple et efficace
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import hashlib
from datetime import datetime
import os

st.set_page_config(
    page_title="Campus Réussite",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_PATH = "campus.db"

# ========== CSS ==========
st.markdown("""
<style>
    body { 
        font-family: 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    }
    
    .header-modern {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 30px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .header-modern h1 { font-size: 2.5em; margin: 0; }
    
    .quiz-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .quiz-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .question-box {
        background: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .progress-bar {
        background: #e0e0e0;
        height: 15px;
        border-radius: 10px;
        overflow: hidden;
        margin: 15px 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        transition: width 0.4s ease;
    }
    
    .score-box {
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 25px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .score-box.success {
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
    }
    
    .score-box.warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }
    
    .score-box.danger {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }
    
    .score-number {
        font-size: 4em;
        font-weight: bold;
        margin: 20px 0;
    }
    
    .correction-correct {
        background: #e8f5e9;
        padding: 20px;
        border-left: 5px solid #4caf50;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    .correction-wrong {
        background: #ffebee;
        padding: 20px;
        border-left: 5px solid #f44336;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    .badge-correct {
        background: #d1fae5;
        color: #065f46;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    .badge-wrong {
        background: #fee2e2;
        color: #7f1d1d;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
        display: inline-block;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ========== DATABASE ==========
class DB:
    def __init__(self):
        self.init()
    
    def init(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
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
        
        c.execute('''CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY, 
            email TEXT UNIQUE,
            password_hash TEXT, 
            nom TEXT, 
            prenom TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'actif')''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY, 
            nom TEXT UNIQUE, 
            description TEXT, 
            nombre_questions INTEGER DEFAULT 0)''')
        
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
        
        c.execute('''CREATE TABLE IF NOT EXISTS resultats (
            id INTEGER PRIMARY KEY, 
            utilisateur_id INTEGER, 
            series_id INTEGER,
            score INTEGER, 
            total INTEGER, 
            pourcentage REAL,
            date_test TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
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
        except:
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

# ========== INIT SESSION ==========
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "user" not in st.session_state:
    st.session_state.user = None
if "current_quiz_state" not in st.session_state:
    st.session_state.current_quiz_state = None

# ========== DISPLAY LOGO ==========
def display_logo():
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo.png", width=150)

# ========== APPRENANT PAGE ==========
def show_apprenant():
    display_logo()
    
    st.markdown("""
    <div class="header-modern">
        <h1>👋 Bienvenue!</h1>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📚 Quizzes", "📊 Résultats", "📝 Feedback"])
    
    with tab1:
        series = db.fa('SELECT * FROM series')
        
        # STATE: Pas en quiz
        if st.session_state.current_quiz_state is None:
            st.subheader("📚 Choisissez une série")
            
            for s in series:
                quizzes = db.fa('SELECT * FROM quiz WHERE series_id=?', (s['id'],))
                
                st.markdown(f"""
                <div class="quiz-card">
                    <h3>{s['nom']}</h3>
                    <p>{s['description']}</p>
                    <p><strong>🎯 {len(quizzes)} questions</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Commencer {s['nom']}", key=f"start_{s['id']}", use_container_width=True):
                    st.session_state.current_quiz_state = {
                        'series_id': s['id'],
                        'series_name': s['nom'],
                        'quizzes': quizzes,
                        'answers': {},
                        'submitted': False
                    }
                    st.rerun()
        
        # STATE: En quiz
        elif st.session_state.current_quiz_state and not st.session_state.current_quiz_state['submitted']:
            state = st.session_state.current_quiz_state
            quizzes = state['quizzes']
            answers = state['answers']
            
            st.subheader(f"📖 {state['series_name']}")
            
            # Barre progression
            progress = len(answers) / len(quizzes) if quizzes else 0
            st.markdown(f"**Progression: {int(progress*100)}%**")
            st.markdown(f'<div class="progress-bar"><div class="progress-fill" style="width: {progress*100}%"></div></div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Questions
            for idx, q in enumerate(quizzes, 1):
                st.markdown(f"""
                <div class="question-box">
                    <h3>Question {idx}/{len(quizzes)}</h3>
                    <h4>{q['question']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                selected = st.radio(
                    "Votre réponse:",
                    ["A", "B", "C", "D"],
                    format_func=lambda x: f"{x}) {[q['option_a'], q['option_b'], q['option_c'], q['option_d']][ord(x)-65]}",
                    key=f"q_{q['id']}",
                    label_visibility="collapsed"
                )
                
                state['answers'][q['id']] = selected
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Retour", use_container_width=True):
                    st.session_state.current_quiz_state = None
                    st.rerun()
            
            with col2:
                if st.button("✅ Soumettre", use_container_width=True, type="primary"):
                    # Marquer comme soumis
                    state['submitted'] = True
                    st.rerun()
        
        # STATE: Résultats affichés
        elif st.session_state.current_quiz_state and st.session_state.current_quiz_state['submitted']:
            state = st.session_state.current_quiz_state
            quizzes = state['quizzes']
            answers = state['answers']
            
            # Calculer le score
            score = 0
            for q in quizzes:
                if q['id'] in answers:
                    if answers[q['id']] in q['reponses_correctes'].split(","):
                        score += 1
            
            percentage = (score / len(quizzes)) * 100
            
            # Sauvegarder dans BD (une seule fois)
            db.q('INSERT INTO resultats (utilisateur_id,series_id,score,total,pourcentage) VALUES (?,?,?,?,?)',
                (st.session_state.user['id'], state['series_id'], score, len(quizzes), percentage))
            
            # Afficher les résultats
            st.subheader(f"📋 Résultats - {state['series_name']}")
            
            # Score box
            if percentage >= 80:
                score_class = "success"
                message = "🎉 Excellent travail!"
            elif percentage >= 60:
                score_class = "warning"
                message = "👍 Bon travail!"
            else:
                score_class = "danger"
                message = "💪 Continuez vos efforts!"
            
            st.markdown(f"""
            <div class="score-box {score_class}">
                <h2>✨ Quiz Complété!</h2>
                <div class="score-number">{score}/{len(quizzes)}</div>
                <div style="font-size: 2em; margin: 10px 0;">{percentage:.1f}%</div>
                <div style="font-size: 1.3em;">{message}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Détails des réponses
            st.subheader("📋 Détail de vos réponses")
            
            for idx, q in enumerate(quizzes, 1):
                user_answer = answers.get(q['id'], 'Non répondu')
                is_correct = user_answer in q['reponses_correctes'].split(",")
                
                if is_correct:
                    st.markdown(f"""
                    <div class="correction-correct">
                        <span class="badge-correct">✅ CORRECT</span>
                        <h4>Q{idx}: {q['question']}</h4>
                        <p><strong>👤 Votre réponse:</strong> {user_answer}) {[q['option_a'], q['option_b'], q['option_c'], q['option_d']][ord(user_answer)-65]}</p>
                        <p><strong>✅ Bonne réponse:</strong> {q['reponses_correctes']}</p>
                        <p style="background: rgba(102, 126, 234, 0.1); padding: 10px; border-radius: 5px; margin-top: 10px;">
                            <strong>💡 Explication:</strong> {q['explication']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="correction-wrong">
                        <span class="badge-wrong">❌ INCORRECT</span>
                        <h4>Q{idx}: {q['question']}</h4>
                        <p><strong>👤 Votre réponse:</strong> {user_answer if user_answer != 'Non répondu' else 'Non répondu'} {f") {[q['option_a'], q['option_b'], q['option_c'], q['option_d']][ord(user_answer)-65]}" if user_answer != 'Non répondu' else ""}</p>
                        <p><strong>✅ Bonne réponse:</strong> {q['reponses_correctes']}</p>
                        <p style="background: rgba(102, 126, 234, 0.1); padding: 10px; border-radius: 5px; margin-top: 10px;">
                            <strong>💡 Explication:</strong> {q['explication']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Recommencer ce quiz", use_container_width=True):
                    st.session_state.current_quiz_state = None
                    st.rerun()
            
            with col2:
                if st.button("📚 Choisir un autre quiz", use_container_width=True):
                    st.session_state.current_quiz_state = None
                    st.rerun()
    
    with tab2:
        st.subheader("📊 Historique")
        
        resultats = db.fa('SELECT * FROM resultats WHERE utilisateur_id=? ORDER BY date_test DESC', 
                          (st.session_state.user['id'],))
        
        if resultats:
            for res in resultats:
                serie = db.f1('SELECT * FROM series WHERE id=?', (res['series_id'],))
                emoji = "🎉" if res['pourcentage'] >= 80 else "👍" if res['pourcentage'] >= 60 else "💪"
                
                st.markdown(f"""
                <div class="quiz-card">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <h4>{emoji} {serie['nom']}</h4>
                            <p>{res['score']}/{res['total']} - {res['date_test']}</p>
                        </div>
                        <div style="text-align: right; font-size: 2em; color: #667eea; font-weight: bold;">
                            {res['pourcentage']:.1f}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Aucun résultat")
    
    with tab3:
        st.subheader("📝 Envoyer un feedback")
        
        titre = st.text_input("Titre")
        msg = st.text_area("Message")
        
        if st.button("Envoyer", use_container_width=True):
            if titre and msg:
                db.q('INSERT INTO feedback (email,titre,message,type) VALUES (?,?,?,?)',
                    (st.session_state.user['email'], titre, msg, "Feedback"))
                st.success("✅ Feedback envoyé!")
            else:
                st.error("❌ Remplissez tous les champs")
    
    st.divider()
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# ========== LOGIN ==========
if not st.session_state.logged_in:
    display_logo()
    
    st.markdown("""
    <div class="header-modern">
        <h1>🎓 Campus Réussite</h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with tab1:
            email = st.text_input("Email")
            pwd = st.text_input("Mot de passe", type="password")
            
            if st.button("Se Connecter", use_container_width=True):
                try:
                    admins_secrets = st.secrets.get("admins", {})
                    if email.lower() in admins_secrets and admins_secrets[email.lower()] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.session_state.user = {'nom':'Admin','prenom':'Principal','email':email.lower(),'id':0}
                        st.rerun()
                except:
                    pass
                
                admin = db.f1('SELECT * FROM admins WHERE email=? AND status="actif"', (email.lower(),))
                if admin and verify_pwd(pwd, admin['password_hash']):
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.user = admin
                    st.rerun()
                
                user = db.f1('SELECT * FROM utilisateurs WHERE email=?', (email.lower(),))
                if user and verify_pwd(pwd, user['password_hash']):
                    if user['status'] == 'bloqué':
                        st.error("Compte bloqué")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.is_admin = False
                        st.rerun()
                else:
                    st.error("Email ou mot de passe incorrect")
        
        with tab2:
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Mot de passe (min 6)", type="password")
            pwd_confirm = st.text_input("Confirmer", type="password")
            
            if st.button("S'inscrire", use_container_width=True):
                if len(password) < 6:
                    st.error("Mot de passe trop court")
                elif password != pwd_confirm:
                    st.error("Mots de passe ne correspondent pas")
                elif not all([nom, prenom, email]):
                    st.error("Remplissez tous les champs")
                else:
                    if db.q('INSERT INTO utilisateurs (nom,prenom,email,password_hash) VALUES (?,?,?,?)',
                        (nom, prenom, email.lower(), hash_pwd(password))):
                        st.success("✅ Inscrit! Connectez-vous.")
                    else:
                        st.error("Email déjà utilisé")

elif st.session_state.logged_in and not st.session_state.is_admin:
    show_apprenant()
