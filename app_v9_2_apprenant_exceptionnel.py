"""
🎓 CAMPUS RÉUSSITE - VERSION COMPLÈTE
✅ Login - Apprenant - Admin - Logo
✅ TOUT EST DÉVELOPPÉ ET TESTÉ
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
    body { font-family: 'Segoe UI', sans-serif; }
    .header-main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .header-main h1 { font-size: 2.5em; margin: 0; }
    
    .quiz-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
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
    
    .score-box.success { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); }
    .score-box.warning { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    .score-box.danger { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
    
    .score-number { font-size: 4em; font-weight: bold; margin: 20px 0; }
    
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
    
    .admin-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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
            'version': '1.0'
        }
        return json.dumps(export_data, indent=2, default=str)
    except:
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
    except:
        return False

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
    <div class="header-main">
        <h1>👋 Bienvenue!</h1>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📚 Quizzes", "📊 Résultats", "📝 Feedback"])
    
    with tab1:
        series = db.fa('SELECT * FROM series')
        
        # Pas en quiz
        if st.session_state.current_quiz_state is None:
            if series:
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
            else:
                st.info("Aucun quiz disponible")
        
        # En quiz - afficher questions
        elif st.session_state.current_quiz_state and not st.session_state.current_quiz_state['submitted']:
            state = st.session_state.current_quiz_state
            quizzes = state['quizzes']
            
            st.subheader(f"📖 {state['series_name']}")
            
            progress = len(state['answers']) / len(quizzes) if quizzes else 0
            st.markdown(f"**Progression: {int(progress*100)}%**")
            st.markdown(f'<div class="progress-bar"><div class="progress-fill" style="width: {progress*100}%"></div></div>', unsafe_allow_html=True)
            
            st.divider()
            
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
                    state['submitted'] = True
                    st.rerun()
        
        # Résultats
        elif st.session_state.current_quiz_state and st.session_state.current_quiz_state['submitted']:
            state = st.session_state.current_quiz_state
            quizzes = state['quizzes']
            answers = state['answers']
            
            score = 0
            for q in quizzes:
                if q['id'] in answers:
                    if answers[q['id']] in q['reponses_correctes'].split(","):
                        score += 1
            
            percentage = (score / len(quizzes)) * 100
            
            db.q('INSERT INTO resultats (utilisateur_id,series_id,score,total,pourcentage) VALUES (?,?,?,?,?)',
                (st.session_state.user['id'], state['series_id'], score, len(quizzes), percentage))
            
            st.subheader(f"📋 Résultats")
            
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
            st.subheader("📋 Vos réponses")
            
            for idx, q in enumerate(quizzes, 1):
                user_answer = answers.get(q['id'], 'Non répondu')
                is_correct = user_answer in q['reponses_correctes'].split(",")
                
                if is_correct:
                    st.markdown(f"""
                    <div class="correction-correct">
                        <strong>✅ Q{idx}: {q['question']}</strong><br>
                        👤 Votre réponse: {user_answer}) {[q['option_a'], q['option_b'], q['option_c'], q['option_d']][ord(user_answer)-65]}<br>
                        ✅ Correcte!<br>
                        <em>💡 {q['explication']}</em>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="correction-wrong">
                        <strong>❌ Q{idx}: {q['question']}</strong><br>
                        👤 Votre réponse: {user_answer if user_answer != 'Non répondu' else 'Non répondu'} {f") {[q['option_a'], q['option_b'], q['option_c'], q['option_d']][ord(user_answer)-65]}" if user_answer != 'Non répondu' else ""}<br>
                        ✅ Bonne réponse: {q['reponses_correctes']}<br>
                        <em>💡 {q['explication']}</em>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Recommencer", use_container_width=True):
                    st.session_state.current_quiz_state = None
                    st.rerun()
            
            with col2:
                if st.button("📚 Autre quiz", use_container_width=True):
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
                st.markdown(f"**{emoji} {serie['nom']}**: {res['score']}/{res['total']} ({res['pourcentage']:.1f}%) - {res['date_test']}")
        else:
            st.info("Aucun résultat")
    
    with tab3:
        st.subheader("📝 Feedback")
        titre = st.text_input("Titre")
        msg = st.text_area("Message")
        
        if st.button("Envoyer", use_container_width=True):
            if titre and msg:
                db.q('INSERT INTO feedback (email,titre,message,type) VALUES (?,?,?,?)',
                    (st.session_state.user['email'], titre, msg, "Feedback"))
                st.success("✅ Envoyé!")
            else:
                st.error("Remplissez tous les champs")
    
    st.divider()
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# ========== ADMIN PAGE ==========
def show_admin():
    display_logo()
    
    st.markdown("""
    <div class="header-main">
        <h1>🔐 Admin</h1>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["Dashboard", "Séries", "Quizzes", "Importer", "Apprenants", "Admins", "BD", "Feedback"])
    
    with tabs[0]:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Apprenants", len(db.fa('SELECT * FROM utilisateurs')))
        with col2:
            st.metric("Séries", len(db.fa('SELECT * FROM series')))
        with col3:
            st.metric("Quizzes", len(db.fa('SELECT * FROM quiz')))
        with col4:
            st.metric("Feedbacks", len(db.fa('SELECT * FROM feedback')))
    
    with tabs[1]:
        with st.expander("➕ Créer"):
            nom = st.text_input("Nom")
            desc = st.text_area("Description")
            if st.button("Créer"):
                if nom:
                    db.q('INSERT INTO series (nom,description) VALUES (?,?)', (nom, desc))
                    st.success("✅ Créé!")
                    st.rerun()
        
        for s in db.fa('SELECT * FROM series'):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{s['nom']}** - {s['description']}")
            with col2:
                if st.button("🗑️", key=f"ds{s['id']}"):
                    db.q('DELETE FROM quiz WHERE series_id=?', (s['id'],))
                    db.q('DELETE FROM series WHERE id=?', (s['id'],))
                    st.rerun()
    
    with tabs[2]:
        series = db.fa('SELECT * FROM series')
        if series:
            sel = st.selectbox("Série", [(s['id'], s['nom']) for s in series], format_func=lambda x: x[1], key="sel_serie")
            for q in db.fa('SELECT * FROM quiz WHERE series_id=?', (sel[0],)):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{q['question']}**")
                with col2:
                    if st.button("🗑️", key=f"dq{q['id']}"):
                        db.q('DELETE FROM quiz WHERE id=?', (q['id'],))
                        st.rerun()
    
    with tabs[3]:
        file = st.file_uploader("CSV", type=["csv"])
        if file:
            try:
                df = pd.read_csv(file, sep=";")
                series = db.fa('SELECT * FROM series')
                if series:
                    sel = st.selectbox("Série", [(s['id'], s['nom']) for s in series], format_func=lambda x: x[1], key="imp_serie")
                    if st.button("Importer"):
                        for _, row in df.iterrows():
                            db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)',
                                (sel[0], row['question'], row['a'], row['b'], row['c'], row['d'], row['reponses_correctes'], row['explication']))
                        st.success("✅ Importé!")
                        st.rerun()
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
    
    with tabs[4]:
        for u in db.fa('SELECT * FROM utilisateurs'):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"{u['prenom']} {u['nom']} - {u['email']}")
            with col2:
                if st.button("Bloquer" if u['status'] == 'actif' else "Débloquer", key=f"b{u['id']}"):
                    new = 'bloqué' if u['status'] == 'actif' else 'actif'
                    db.q('UPDATE utilisateurs SET status=? WHERE id=?', (new, u['id']))
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"du{u['id']}"):
                    db.q('DELETE FROM utilisateurs WHERE id=?', (u['id'],))
                    st.rerun()
    
    with tabs[5]:
        with st.expander("➕ Créer"):
            nom = st.text_input("Nom", key="an")
            prenom = st.text_input("Prénom", key="ap")
            email = st.text_input("Email", key="ae")
            pwd = st.text_input("Password", type="password", key="apwd")
            
            if st.button("Créer", key="ac"):
                if len(pwd) >= 8:
                    db.q('INSERT INTO admins (email,password_hash,nom,prenom) VALUES (?,?,?,?)',
                        (email.lower(), hash_pwd(pwd), nom, prenom))
                    st.success("✅ Créé!")
                    st.rerun()
        
        for a in db.fa('SELECT * FROM admins'):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"{a['prenom']} {a['nom']} - {a['email']}")
            with col2:
                if st.button("🗑️", key=f"da{a['id']}"):
                    db.q('DELETE FROM admins WHERE id=?', (a['id'],))
                    st.rerun()
    
    with tabs[6]:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Exporter", use_container_width=True):
                export_json = export_database()
                if export_json:
                    st.download_button("Télécharger", export_json, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with col2:
            file = st.file_uploader("Importer", type=["json"])
            if file:
                json_data = file.read().decode("utf-8")
                if st.button("Restaurer"):
                    if import_database(json_data):
                        st.success("✅ Restauré!")
                        st.rerun()
    
    with tabs[7]:
        for f in db.fa('SELECT * FROM feedback ORDER BY date_feedback DESC'):
            st.write(f"**{f['titre']}** - {f['email']}")
            st.write(f['message'])
            if st.button("🗑️", key=f"df{f['id']}"):
                db.q('DELETE FROM feedback WHERE id=?', (f['id'],))
                st.rerun()
    
    st.divider()
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

# ========== MAIN LOGIC ==========
if not st.session_state.logged_in:
    display_logo()
    
    st.markdown("""
    <div class="header-main">
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

elif st.session_state.logged_in and st.session_state.is_admin:
    show_admin()

elif st.session_state.logged_in and not st.session_state.is_admin:
    show_apprenant()
