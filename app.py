"""
🎓 CAMPUS RÉUSSITE v8.2 FINAL
- Inscription sans auto-connexion
- Password hashing correct
- Table quiz_pending corrigée
- Admin access sécurisé
- Import + Approbation/Rejet
"""

import streamlit as st
import sqlite3
import pandas as pd
import re
import os
import hashlib
from datetime import datetime, timedelta

st.set_page_config(page_title="Campus Réussite", layout="wide", initial_sidebar_state="expanded")

DB_PATH = os.path.join(os.path.dirname(__file__), "campus.db")

# ========== DATABASE ==========
class Database:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Utilisateurs (passwords hashés)
        cursor.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'apprenant',
            status TEXT DEFAULT 'actif',
            session_duration_minutes INTEGER DEFAULT 120,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Sessions
        cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        )''')
        
        # Audit logs
        cursor.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        )''')
        
        # Failed logins
        cursor.execute('''CREATE TABLE IF NOT EXISTS failed_logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Séries
        cursor.execute('''CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            description TEXT,
            nombre_questions INTEGER DEFAULT 50,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Quiz
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
        
        # Quiz en attente d'approbation
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
            date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Résultats
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
        
        # Feedback
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

# ========== SÉCURITÉ ==========
def hash_password(password):
    """Hasher le password avec SHA256 + salt"""
    salt = "campus_reussite_2024"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(password, hash_stored):
    """Vérifier le password"""
    return hash_password(password) == hash_stored

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def sanitize_input(text):
    dangerous = ['<', '>', '"', "'", '{', '}']
    for char in dangerous:
        text = text.replace(char, '')
    return text.strip()

# ========== FONCTIONS UTILITAIRES ==========
def add_user(nom, prenom, email, username, password):
    """Ajouter un utilisateur"""
    try:
        password_hash = hash_password(password)
        db.query(
            'INSERT INTO utilisateurs (nom, prenom, email, username, password_hash, role) VALUES (?, ?, ?, ?, ?, ?)',
            (sanitize_input(nom), sanitize_input(prenom), email.lower(), sanitize_input(username), password_hash, 'apprenant')
        )
        return True
    except:
        return False

def get_user_by_email(email):
    return db.fetch_one('SELECT * FROM utilisateurs WHERE email = ?', (email.lower(),))

def toggle_user_status(user_id):
    user = db.fetch_one('SELECT status FROM utilisateurs WHERE id = ?', (user_id,))
    new_status = 'bloqué' if user['status'] == 'actif' else 'actif'
    db.query('UPDATE utilisateurs SET status = ? WHERE id = ?', (new_status, user_id))
    if new_status == 'bloqué':
        db.query('DELETE FROM sessions WHERE utilisateur_id = ?', (user_id,))

def set_session_duration(user_id, duration):
    if 5 <= duration <= 1440:
        db.query('UPDATE utilisateurs SET session_duration_minutes = ? WHERE id = ?', (duration, user_id))
        return True
    return False

def get_all_users():
    return db.fetch_all('SELECT * FROM utilisateurs WHERE role = "apprenant" ORDER BY date_creation DESC')

def add_series(nom, description, nombre_q=50):
    try:
        db.query('INSERT INTO series (nom, description, nombre_questions) VALUES (?, ?, ?)',
                (sanitize_input(nom), sanitize_input(description), nombre_q))
        return True
    except:
        return False

def get_all_series():
    return db.fetch_all('SELECT * FROM series ORDER BY date_creation DESC')

def get_quiz_by_series(series_id):
    return db.fetch_all('SELECT * FROM quiz WHERE series_id = ? ORDER BY ordre', (series_id,))

def add_quiz_to_series(series_id, question, a, b, c, d, correct, exp):
    db.query(
        'INSERT INTO quiz (series_id, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, ordre) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (series_id, sanitize_input(question), sanitize_input(a), sanitize_input(b), sanitize_input(c), sanitize_input(d), correct, sanitize_input(exp), 0)
    )

def add_quiz_pending(question, a, b, c, d, correct, exp, cat):
    db.query(
        'INSERT INTO quiz_pending (question, option_a, option_b, option_c, option_d, reponses_correctes, explication, categorie) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (sanitize_input(question), sanitize_input(a), sanitize_input(b), sanitize_input(c), sanitize_input(d), correct, sanitize_input(exp), cat)
    )

def get_pending_quizzes():
    return db.fetch_all('SELECT * FROM quiz_pending ORDER BY date_import DESC')

def approve_quiz(pending_id, series_id):
    quiz = db.fetch_one('SELECT * FROM quiz_pending WHERE id = ?', (pending_id,))
    if quiz:
        add_quiz_to_series(series_id, quiz['question'], quiz['option_a'], quiz['option_b'],
                          quiz['option_c'], quiz['option_d'], quiz['reponses_correctes'], quiz['explication'])
        db.query('DELETE FROM quiz_pending WHERE id = ?', (pending_id,))
        return True
    return False

def reject_quiz(pending_id):
    db.query('DELETE FROM quiz_pending WHERE id = ?', (pending_id,))

def save_series_result(user_id, series_id, score, total):
    pct = (score / total * 100) if total > 0 else 0
    db.query(
        'INSERT INTO resultats (utilisateur_id, series_id, score, total, pourcentage) VALUES (?, ?, ?, ?, ?)',
        (user_id, series_id, score, total, pct)
    )

# ========== CSS ==========
st.markdown("""
<style>
    .header-title {
        background: linear-gradient(135deg, #1a5f3d 0%, #d4a574 100%);
        color: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(26, 95, 61, 0.3); text-align: center;
    }
    .stat-box {
        background: linear-gradient(135deg, #1a5f3d 0%, #d4a574 100%);
        color: white; padding: 1.5rem; border-radius: 12px; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .stat-number { font-size: 2.5rem; font-weight: 700; }
    .stat-label { font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem; }
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
if "pre_fill_email" not in st.session_state:
    st.session_state.pre_fill_email = ""
if "pre_fill_password" not in st.session_state:
    st.session_state.pre_fill_password = ""

# ========== PAGE AUTHENTIFICATION ==========
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="header-title">
            <h1>🎓 Campus Réussite</h1>
            <p>Plateforme d'Apprentissage</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with tab1:
            st.markdown("### Connexion")
            
            email = st.text_input("Email", value=st.session_state.pre_fill_email, key="login_email")
            pwd = st.text_input("Mot de passe", type="password", value=st.session_state.pre_fill_password, key="login_pwd")
            
            if st.button("Se Connecter", use_container_width=True, type="primary"):
                # Vérifier admin d'abord
                try:
                    admins = st.secrets.get("admins", {})
                    if email.lower() in admins and admins[email.lower()] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.user = {'nom': 'Admin', 'prenom': 'Campus', 'email': email.lower(), 'role': 'admin', 'id': 0}
                        st.session_state.is_admin = True
                        st.rerun()
                except:
                    pass
                
                # Vérifier apprenant
                user = get_user_by_email(email.lower())
                
                if user and verify_password(pwd, user['password_hash']):
                    if user['status'] == 'bloqué':
                        st.error("❌ Votre compte a été bloqué")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.is_admin = False
                        st.session_state.pre_fill_email = ""
                        st.session_state.pre_fill_password = ""
                        st.rerun()
                else:
                    st.error("❌ Email ou mot de passe incorrect")
        
        with tab2:
            st.markdown("### Créer un Compte")
            
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
                elif password != pwd_confirm:
                    st.error("❌ Mots de passe différents")
                elif get_user_by_email(email.lower()):
                    st.error("❌ Email déjà utilisé")
                elif add_user(nom, prenom, email.lower(), username, password):
                    st.success("✅ Compte créé!")
                    st.session_state.pre_fill_email = email.lower()
                    st.session_state.pre_fill_password = password
                    st.info("➡️ Allez à l'onglet 'Connexion' et cliquez sur 'Se Connecter'")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la création")

# ========== APPLICATION PRINCIPALE ==========
else:
    user = st.session_state.user
    is_admin = st.session_state.is_admin
    
    st.markdown(f"""
    <div class="header-title">
        <h1>🎓 Campus Réussite</h1>
        <p>{'👮 Admin' if is_admin else '👨‍🎓 Apprenant'}: {user['prenom']} {user['nom']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown(f"👤 **{user['prenom']} {user['nom']}**")
        st.markdown(f"📧 {user['email']}")
        st.divider()
        
        if is_admin:
            st.markdown("### 🎛️ Admin")
            if st.button("👨‍🎓 Mode Apprenant"):
                st.session_state.is_admin = False
                st.session_state.current_page = "accueil"
                st.rerun()
        
        st.divider()
        if st.button("🚪 Déconnexion"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.is_admin = False
            st.session_state.pre_fill_email = ""
            st.session_state.pre_fill_password = ""
            st.rerun()
    
    # ========== MODE APPRENANT ==========
    if not is_admin:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🏠 Accueil", use_container_width=True):
                st.session_state.current_page = "accueil"
                st.rerun()
        with col2:
            if st.button("📚 Séries", use_container_width=True):
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
        
        if st.session_state.current_page == "accueil":
            all_series = get_all_series()
            results = db.fetch_all('SELECT * FROM resultats WHERE utilisateur_id = ?', (user['id'],))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(all_series)}</div><div class="stat-label">Séries</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(results)}</div><div class="stat-label">Complétées</div></div>', unsafe_allow_html=True)
            with col3:
                pct = (len(results) / len(all_series) * 100) if all_series else 0
                st.markdown(f'<div class="stat-box"><div class="stat-number">{pct:.0f}%</div><div class="stat-label">Progression</div></div>', unsafe_allow_html=True)
            
            st.divider()
            if all_series:
                for series in all_series:
                    result = next((r for r in results if r['series_id'] == series['id']), None)
                    status = f"✅ {result['score']}/{result['total']}" if result else "⏳ À faire"
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{series['nom']}** - {series['nombre_questions']} q. - {status}")
                    with col2:
                        if st.button("Commencer", key=f"s_{series['id']}", use_container_width=True):
                            st.session_state.current_page = f"series_{series['id']}"
                            st.rerun()
        
        elif st.session_state.current_page == "series":
            st.markdown("### 📚 Mes Séries")
            all_series = get_all_series()
            results = db.fetch_all('SELECT * FROM resultats WHERE utilisateur_id = ?', (user['id'],))
            
            if all_series:
                for series in all_series:
                    result = next((r for r in results if r['series_id'] == series['id']), None)
                    st.markdown(f"**{series['nom']}** ({series['nombre_questions']} questions)")
                    if result:
                        st.success(f"✅ Score: {result['score']}/{result['total']} ({result['pourcentage']:.0f}%)")
                    if st.button("Faire", key=f"btn_{series['id']}", use_container_width=True):
                        st.session_state.current_page = f"series_{series['id']}"
                        st.rerun()
                    st.divider()
        
        elif st.session_state.current_page == "resultats":
            st.markdown("### 📊 Mes Résultats")
            results = db.fetch_all('SELECT * FROM resultats WHERE utilisateur_id = ? ORDER BY date_completion DESC', (user['id'],))
            if results:
                df = pd.DataFrame([{
                    'Série': db.fetch_one('SELECT nom FROM series WHERE id = ?', (r['series_id'],))['nom'],
                    'Score': f"{r['score']}/{r['total']}",
                    '%': f"{r['pourcentage']:.0f}%"
                } for r in results])
                st.dataframe(df, use_container_width=True, hide_index=True)
        
        elif st.session_state.current_page == "feedback":
            st.markdown("### 💬 Feedback")
            with st.form("f"):
                titre = st.text_input("Titre")
                msg = st.text_area("Message")
                if st.form_submit_button("Envoyer", use_container_width=True):
                    if titre and msg:
                        db.query('INSERT INTO feedback (email, titre, message, type) VALUES (?, ?, ?, ?)',
                                (user['email'], sanitize_input(titre), sanitize_input(msg), "Feedback"))
                        st.success("✅ Enregistré!")
        
        elif st.session_state.current_page.startswith("series_"):
            series_id = int(st.session_state.current_page.split("_")[1])
            series = db.fetch_one('SELECT * FROM series WHERE id = ?', (series_id,))
            quiz_list = get_quiz_by_series(series_id)
            
            st.markdown(f"### 🎯 {series['nom']}")
            
            if f"answers_{series_id}" not in st.session_state:
                st.session_state[f"answers_{series_id}"] = {}
            
            for idx, quiz in enumerate(quiz_list):
                st.markdown(f"**Q{idx+1}/{len(quiz_list)}: {quiz['question']}**")
                options = [quiz['option_a'], quiz['option_b'], quiz['option_c'], quiz['option_d']]
                selected = st.multiselect("Réponses:", options, default=st.session_state[f"answers_{series_id}"].get(quiz['id'], []), key=f"q_{quiz['id']}")
                st.session_state[f"answers_{series_id}"][quiz['id']] = selected
                st.divider()
            
            if st.button("✅ VALIDER", use_container_width=True, type="primary"):
                if len(st.session_state[f"answers_{series_id}"]) < len(quiz_list):
                    st.error("❌ Répondez à TOUTES!")
                else:
                    score = 0
                    for quiz in quiz_list:
                        correct = [c.strip() for c in quiz['reponses_correctes'].split(',')]
                        if set(st.session_state[f"answers_{series_id}"][quiz['id']]) == set(correct):
                            score += 1
                    
                    save_series_result(user['id'], series_id, score, len(quiz_list))
                    st.success(f"✅ Score: {score}/{len(quiz_list)} ({score/len(quiz_list)*100:.0f}%)")
                    st.balloons()
                    
                    st.divider()
                    st.markdown("### 📝 Corrections")
                    for idx, quiz in enumerate(quiz_list):
                        correct = [c.strip() for c in quiz['reponses_correctes'].split(',')]
                        your = st.session_state[f"answers_{series_id}"][quiz['id']]
                        with st.expander(f"Q{idx+1}: {quiz['question']}"):
                            st.markdown(f"**Votre réponse:** {', '.join(your) if your else 'Non répondue'}")
                            st.markdown(f"**Correcte:** {', '.join(correct)}")
                            st.markdown(f"💡 {quiz['explication']}")
                    
                    if st.button("🏠 Retour"):
                        st.session_state.current_page = "accueil"
                        st.rerun()
    
    # ========== MODE ADMIN ==========
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
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
        
        st.divider()
        
        if st.session_state.admin_tab == "dashboard":
            st.markdown("### 📊 Statistiques")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(get_all_users())}</div><div class="stat-label">Apprenants</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(get_all_series())}</div><div class="stat-label">Séries</div></div>', unsafe_allow_html=True)
            with col3:
                total = sum(len(get_quiz_by_series(s['id'])) for s in get_all_series())
                st.markdown(f'<div class="stat-box"><div class="stat-number">{total}</div><div class="stat-label">Quizzes</div></div>', unsafe_allow_html=True)
            with col4:
                fb = db.fetch_all('SELECT * FROM feedback')
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(fb)}</div><div class="stat-label">Feedbacks</div></div>', unsafe_allow_html=True)
        
        elif st.session_state.admin_tab == "series":
            st.markdown("### 📚 Gestion Séries")
            
            with st.expander("➕ Créer Série"):
                nom = st.text_input("Nom")
                desc = st.text_area("Description")
                nq = st.slider("Questions", 1, 100, 50)
                if st.button("Créer", use_container_width=True):
                    if nom and add_series(nom, desc, nq):
                        st.success("✅ Créée!")
                        st.rerun()
            
            st.divider()
            st.markdown("### ➕ Ajouter Quiz")
            series = get_all_series()
            if series:
                sel = st.selectbox("Série", [(s['id'], s['nom']) for s in series], format_func=lambda x: x[1])
                with st.form("add_q"):
                    q = st.text_input("Question")
                    a = st.text_input("A")
                    b = st.text_input("B")
                    c = st.text_input("C")
                    d = st.text_input("D")
                    correct = st.multiselect("Correctes", ["A", "B", "C", "D"])
                    exp = st.text_area("Explication")
                    if st.form_submit_button("Ajouter", use_container_width=True):
                        if all([q, a, b, c, d, correct, exp]):
                            add_quiz_to_series(sel[0], q, a, b, c, d, ", ".join(correct), exp)
                            st.success("✅ Ajouté!")
                            st.rerun()
        
        elif st.session_state.admin_tab == "import":
            st.markdown("### 📤 Importer des Quizzes")
            
            uploaded = st.file_uploader("CSV", type=["csv"])
            if uploaded:
                try:
                    df = pd.read_csv(uploaded, sep=";")
                    st.success(f"✅ {len(df)} lignes")
                    st.dataframe(df, use_container_width=True)
                    
                    series_list = get_all_series()
                    if series_list:
                        selected = st.selectbox("Série", [(s['id'], s['nom']) for s in series_list], format_func=lambda x: x[1])
                        if st.button("Ajouter", use_container_width=True, type="primary"):
                            for _, row in df.iterrows():
                                add_quiz_pending(row['question'], row['a'], row['b'], row['c'], row['d'],
                                               row['reponses_correctes'], row['explication'], selected[1])
                            st.success(f"✅ En attente d'approbation!")
                            st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
            
            st.divider()
            st.markdown("### ✅ En Attente d'Approbation")
            
            pending = get_pending_quizzes()
            if pending:
                st.write(f"**{len(pending)} quizzes**")
                for idx, pend in enumerate(pending):
                    st.markdown(f"**Q{idx+1}: {pend['question']}**")
                    st.markdown(f"A) {pend['option_a']} | B) {pend['option_b']} | C) {pend['option_c']} | D) {pend['option_d']}")
                    st.markdown(f"Correctes: {pend['reponses_correctes']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Approuver", key=f"app_{pend['id']}_{idx}", use_container_width=True):
                            series = db.fetch_one('SELECT id FROM series WHERE nom = ?', (pend['categorie'],))
                            if not series:
                                add_series(pend['categorie'], "", 50)
                                series = db.fetch_one('SELECT id FROM series WHERE nom = ?', (pend['categorie'],))
                            approve_quiz(pend['id'], series['id'])
                            st.success("✅ Approuvé!")
                            st.rerun()
                    with col2:
                        if st.button("❌ Rejeter", key=f"rej_{pend['id']}_{idx}", use_container_width=True):
                            reject_quiz(pend['id'])
                            st.info("❌ Rejeté")
                            st.rerun()
                    st.divider()
        
        elif st.session_state.admin_tab == "users":
            st.markdown("### 👥 Apprenants")
            users = get_all_users()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(users))
            with col2:
                st.metric("Actifs", len([u for u in users if u['status'] == 'actif']))
            with col3:
                st.metric("Bloqués", len([u for u in users if u['status'] == 'bloqué']))
            
            st.divider()
            if users:
                for u in users:
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    with col1:
                        icon = "✅" if u['status'] == 'actif' else "🔒"
                        st.markdown(f"{icon} **{u['prenom']} {u['nom']}**")
                        st.caption(f"Session: {u['session_duration_minutes']}min")
                    with col2:
                        if st.button("Bloquer" if u['status'] == 'actif' else "Débloquer", key=f"t_{u['id']}", use_container_width=True):
                            toggle_user_status(u['id'])
                            st.rerun()
                    with col3:
                        dur = st.number_input("Min", 5, 1440, u['session_duration_minutes'], key=f"d_{u['id']}")
                        if dur != u['session_duration_minutes']:
                            set_session_duration(u['id'], int(dur))
                            st.rerun()
                    with col4:
                        if st.button("Révoquer", key=f"r_{u['id']}", use_container_width=True):
                            db.query('DELETE FROM sessions WHERE utilisateur_id = ?', (u['id'],))
                            st.info("Révoqué")
                    st.divider()
        
        elif st.session_state.admin_tab == "feedback":
            st.markdown("### 💬 Feedback")
            fb_list = db.fetch_all('SELECT * FROM feedback ORDER BY date_creation DESC')
            if fb_list:
                for fb in fb_list:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{fb['titre']}**")
                        st.markdown(f"📧 {fb['email']}")
                        st.markdown(f"{fb['message']}")
                    with col2:
                        st.caption(fb['date_creation'][:10])
                    st.divider()
