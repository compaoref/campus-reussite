"""
🎓 CAMPUS RÉUSSITE v9.3 - SIMPLE ET FONCTIONNEL
✅ Bug Résultats FIXÉ - Affichage fonctionne!
✅ Logo.png affichage simple
✅ Corrections claires
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
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
    }
    .header-main h1 { font-size: 2.5em; margin: 0; }
    .card { background: white; padding: 20px; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    .score-box { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); color: white; padding: 30px; border-radius: 15px; text-align: center; margin: 20px 0; }
    .score-box.orange { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    .score-box.red { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
    .score-number { font-size: 3em; font-weight: bold; }
    .correction-correct { background: #e8f5e9; padding: 15px; border-left: 5px solid #4caf50; margin: 10px 0; border-radius: 5px; }
    .correction-wrong { background: #ffebee; padding: 15px; border-left: 5px solid #f44336; margin: 10px 0; border-radius: 5px; }
    .logo-container { text-align: center; margin: 20px 0; }
    .logo-container img { max-width: 150px; height: auto; border-radius: 10px; }
    .question-box { background: #f5f5f5; padding: 20px; margin: 15px 0; border-radius: 10px; border-left: 5px solid #667eea; }
    .progress-bar { background: #e0e0e0; height: 20px; border-radius: 10px; margin: 10px 0; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; }
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
            'version': '9.3'
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
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "editing_quiz_id" not in st.session_state:
    st.session_state.editing_quiz_id = None
if "current_series_id" not in st.session_state:
    st.session_state.current_series_id = None
if "current_quizzes" not in st.session_state:
    st.session_state.current_quizzes = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None

check_session_timeout()
update_activity()

# ========== LOGIN ==========
if not st.session_state.logged_in:
    
    # Afficher le logo
    st.markdown('<div class="logo-container"><img src="logo.png" alt="Logo"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="header-main">
        <h1>🎓 Campus Réussite</h1>
        <p>Plateforme d'apprentissage</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with tab1:
            st.subheader("Connexion")
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
            st.subheader("Inscription")
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Mot de passe (min 6)", type="password", key="reg_pwd")
            pwd_confirm = st.text_input("Confirmer", type="password", key="reg_confirm")
            
            if st.button("S'inscrire", use_container_width=True):
                if len(password) < 6:
                    st.error("Mot de passe trop court")
                elif password != pwd_confirm:
                    st.error("Mots de passe ne correspondent pas")
                elif not nom or not prenom or not email:
                    st.error("Remplissez tous les champs")
                else:
                    if db.q('INSERT INTO utilisateurs (nom,prenom,email,password_hash) VALUES (?,?,?,?)',
                        (nom, prenom, email.lower(), hash_pwd(password))):
                        st.success("Compte créé! Connectez-vous.")
                    else:
                        st.error("Email déjà utilisé")

# ========== APPRENANT ==========
elif st.session_state.logged_in and not st.session_state.is_admin:
    
    # Logo
    st.markdown('<div class="logo-container"><img src="logo.png" alt="Logo"></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="header-main">
        <h1>👋 Bienvenue {st.session_state.user['prenom']}!</h1>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📚 Quizzes", "📊 Résultats", "📝 Feedback"])
    
    # TAB 1: QUIZZES
    with tab1:
        series = db.fa('SELECT * FROM series')
        
        if not st.session_state.quiz_submitted:
            st.subheader("Sélectionnez un quiz")
            
            for s in series:
                quizzes = db.fa('SELECT * FROM quiz WHERE series_id=?', (s['id'],))
                st.markdown(f"**{s['nom']}** - {len(quizzes)} questions", help=s['description'])
                
                if st.button(f"Commencer", key=f"start_{s['id']}", use_container_width=True):
                    st.session_state.current_series_id = s['id']
                    st.session_state.current_quizzes = quizzes
                    st.session_state.quiz_answers = {}
                    st.rerun()
            
            # Quiz en cours
            if st.session_state.current_quizzes:
                st.divider()
                quizzes = st.session_state.current_quizzes
                
                # Barre progression
                progress = len(st.session_state.quiz_answers) / len(quizzes)
                st.markdown(f"Progression: {int(progress*100)}%")
                st.markdown(f'<div class="progress-bar"><div class="progress-fill" style="width: {progress*100}%"></div></div>', unsafe_allow_html=True)
                
                # Questions
                for idx, q in enumerate(quizzes, 1):
                    st.markdown(f'<div class="question-box"><strong>Q{idx}/{len(quizzes)}: {q["question"]}</strong></div>', unsafe_allow_html=True)
                    
                    selected = st.radio(
                        "Réponse:",
                        ["A", "B", "C", "D"],
                        format_func=lambda x: f"{x}) {[q['option_a'], q['option_b'], q['option_c'], q['option_d']][ord(x)-65]}",
                        key=f"q_{q['id']}",
                        label_visibility="collapsed"
                    )
                    
                    st.session_state.quiz_answers[q['id']] = selected
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Retour", use_container_width=True):
                        st.session_state.current_quizzes = []
                        st.session_state.quiz_answers = {}
                        st.rerun()
                
                with col2:
                    if st.button("Soumettre les réponses", use_container_width=True, type="primary"):
                        score = 0
                        for q in quizzes:
                            if q['id'] in st.session_state.quiz_answers:
                                if st.session_state.quiz_answers[q['id']] in q['reponses_correctes'].split(","):
                                    score += 1
                        
                        percentage = (score / len(quizzes)) * 100
                        
                        # Sauvegarder
                        db.q('INSERT INTO resultats (utilisateur_id,series_id,score,total,pourcentage) VALUES (?,?,?,?,?)',
                            (st.session_state.user['id'], st.session_state.current_series_id, score, len(quizzes), percentage))
                        
                        st.session_state.quiz_submitted = True
                        st.session_state.current_result = {
                            'score': score,
                            'total': len(quizzes),
                            'percentage': percentage,
                            'quizzes': quizzes
                        }
                        st.rerun()
        
        # AFFICHAGE DES RÉSULTATS - SIMPLE ET DIRECT
        if st.session_state.quiz_submitted and st.session_state.current_result:
            result = st.session_state.current_result
            quizzes = result['quizzes']
            score = result['score']
            total = result['total']
            percentage = result['percentage']
            
            # Score spectaculaire
            if percentage >= 80:
                score_class = "score-box"
                message = "🎉 Excellent travail!"
            elif percentage >= 60:
                score_class = "score-box orange"
                message = "👍 Bon travail!"
            else:
                score_class = "score-box red"
                message = "💪 Continuez vos efforts!"
            
            st.markdown(f'''
            <div class="{score_class}">
                <h2>✨ Quiz Complété!</h2>
                <div class="score-number">{score}/{total}</div>
                <div style="font-size: 2em; margin: 10px 0;">{percentage:.1f}%</div>
                <div style="font-size: 1.3em;">{message}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            st.divider()
            st.subheader("📋 Détail de vos réponses")
            
            # Afficher chaque question et réponse
            for idx, q in enumerate(quizzes, 1):
                user_answer = st.session_state.quiz_answers.get(q['id'], 'Non répondu')
                is_correct = user_answer in q['reponses_correctes'].split(",")
                
                if is_correct:
                    st.markdown(f'''
                    <div class="correction-correct">
                        <strong>✅ Q{idx}: {q['question']}</strong><br>
                        👤 Votre réponse: <strong>{user_answer}</strong>) {[q['option_a'], q['option_b'], q['option_c'], q['option_d']][ord(user_answer)-65]}<br>
                        ✅ Correcte!<br>
                        <em>💡 {q['explication']}</em>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div class="correction-wrong">
                        <strong>❌ Q{idx}: {q['question']}</strong><br>
                        👤 Votre réponse: <strong>{user_answer if user_answer != 'Non répondu' else 'Non répondu'}</strong> {f") {[q['option_a'], q['option_b'], q['option_c'], q['option_d']][ord(user_answer)-65]}" if user_answer != 'Non répondu' else ""}<br>
                        ✅ Bonne réponse: <strong>{q['reponses_correctes']}</strong><br>
                        <em>💡 {q['explication']}</em>
                    </div>
                    ''', unsafe_allow_html=True)
            
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Recommencer ce quiz", use_container_width=True):
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers = {}
                    st.session_state.current_result = None
                    st.rerun()
            
            with col2:
                if st.button("Choisir un autre quiz", use_container_width=True):
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers = {}
                    st.session_state.current_result = None
                    st.session_state.current_quizzes = []
                    st.rerun()
    
    # TAB 2: RÉSULTATS
    with tab2:
        st.subheader("Historique")
        
        resultats = db.fa('SELECT * FROM resultats WHERE utilisateur_id=? ORDER BY date_test DESC', 
                          (st.session_state.user['id'],))
        
        if resultats:
            for res in resultats:
                serie = db.f1('SELECT * FROM series WHERE id=?', (res['series_id'],))
                st.markdown(f"**{serie['nom']}**: {res['score']}/{res['total']} ({res['pourcentage']:.1f}%) - {res['date_test']}")
        else:
            st.info("Aucun résultat")
    
    # TAB 3: FEEDBACK
    with tab3:
        st.subheader("Envoyer un feedback")
        
        titre = st.text_input("Titre")
        msg = st.text_area("Message")
        
        if st.button("Envoyer", use_container_width=True):
            if titre and msg:
                db.q('INSERT INTO feedback (email,titre,message,type) VALUES (?,?,?,?)',
                    (st.session_state.user['email'], titre, msg, "Feedback"))
                st.success("✅ Envoyé!")
            else:
                st.error("Remplissez tous les champs")
    
    if st.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# ========== ADMIN ==========
elif st.session_state.logged_in and st.session_state.is_admin:
    
    # Logo
    st.markdown('<div class="logo-container"><img src="logo.png" alt="Logo"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="header-main">
        <h1>🔐 Admin</h1>
    </div>
    """, unsafe_allow_html=True)
    
    admin_tabs = st.tabs(["Dashboard", "Séries", "Quizzes", "Importer", "Apprenants", "Admins", "BD", "Feedback"])
    
    # DASHBOARD
    with admin_tabs[0]:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Apprenants", len(db.fa('SELECT * FROM utilisateurs')))
        with col2:
            st.metric("Séries", len(db.fa('SELECT * FROM series')))
        with col3:
            st.metric("Quizzes", len(db.fa('SELECT * FROM quiz')))
        with col4:
            st.metric("Feedbacks", len(db.fa('SELECT * FROM feedback')))
    
    # SÉRIES
    with admin_tabs[1]:
        st.subheader("Séries")
        
        with st.expander("Créer"):
            nom = st.text_input("Nom")
            desc = st.text_area("Description")
            if st.button("Créer"):
                if nom:
                    db.q('INSERT INTO series (nom,description) VALUES (?,?)', (nom, desc))
                    st.rerun()
        
        for s in db.fa('SELECT * FROM series'):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{s['nom']}** - {s['description']}")
            with col2:
                if st.button("Supprimer", key=f"del_s_{s['id']}"):
                    db.q('DELETE FROM quiz WHERE series_id=?', (s['id'],))
                    db.q('DELETE FROM series WHERE id=?', (s['id'],))
                    st.rerun()
    
    # QUIZZES
    with admin_tabs[2]:
        st.subheader("Quizzes")
        
        series = db.fa('SELECT * FROM series')
        if series:
            selected_series = st.selectbox("Série", [(s['id'], s['nom']) for s in series], format_func=lambda x: x[1])
            
            for q in db.fa('SELECT * FROM quiz WHERE series_id=?', (selected_series[0],)):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{q['question']}**")
                    st.caption(f"A) {q['option_a']} B) {q['option_b']} C) {q['option_c']} D) {q['option_d']}")
                with col2:
                    if st.button("Supprimer", key=f"del_q_{q['id']}"):
                        db.q('DELETE FROM quiz WHERE id=?', (q['id'],))
                        st.rerun()
    
    # IMPORTER
    with admin_tabs[3]:
        st.subheader("Importer CSV")
        
        file = st.file_uploader("CSV", type=["csv"])
        if file:
            try:
                df = pd.read_csv(file, sep=";")
                st.write(f"{len(df)} quizzes")
                
                series = db.fa('SELECT * FROM series')
                if series:
                    sel = st.selectbox("Série", [(s['id'], s['nom']) for s in series], format_func=lambda x: x[1], key="imp")
                    
                    if st.button("Importer"):
                        for _, row in df.iterrows():
                            db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)',
                                (sel[0], row['question'], row['a'], row['b'], row['c'], row['d'], row['reponses_correctes'], row['explication']))
                        st.success("✅ Importé!")
                        st.rerun()
            except:
                st.error("Erreur")
    
    # APPRENANTS
    with admin_tabs[4]:
        st.subheader("Apprenants")
        
        for u in db.fa('SELECT * FROM utilisateurs'):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"{u['prenom']} {u['nom']} - {u['email']}")
            with col2:
                if st.button("Bloquer" if u['status'] == 'actif' else "Débloquer", key=f"b_{u['id']}"):
                    new = 'bloqué' if u['status'] == 'actif' else 'actif'
                    db.q('UPDATE utilisateurs SET status=? WHERE id=?', (new, u['id']))
                    st.rerun()
            with col3:
                if st.button("Supprimer", key=f"d_{u['id']}"):
                    db.q('DELETE FROM utilisateurs WHERE id=?', (u['id'],))
                    st.rerun()
    
    # ADMINS
    with admin_tabs[5]:
        st.subheader("Administrateurs")
        
        with st.expander("Créer"):
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
                if st.button("Supprimer", key=f"da_{a['id']}"):
                    db.q('DELETE FROM admins WHERE id=?', (a['id'],))
                    st.rerun()
    
    # BD
    with admin_tabs[6]:
        st.subheader("Base de Données")
        
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
    
    # FEEDBACK
    with admin_tabs[7]:
        st.subheader("Feedback")
        
        for f in db.fa('SELECT * FROM feedback ORDER BY date_feedback DESC'):
            st.write(f"**{f['titre']}** - {f['email']}")
            st.write(f['message'])
            if st.button("Supprimer", key=f"df_{f['id']}"):
                db.q('DELETE FROM feedback WHERE id=?', (f['id'],))
                st.rerun()
    
    if st.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()
