"""
🎓 CAMPUS RÉUSSITE v8.1 NO DEPENDENCIES
Plateforme Sécurisée - ZÉRO Installation Requise
SHA256 Hashing (Intégré Python)
Sessions Gérées + Logs d'Audit + Rate Limiting
"""

import streamlit as st
import sqlite3
import pandas as pd
import re
import os
import hashlib
from datetime import datetime, timedelta

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
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS failed_logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            ip_address TEXT,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            description TEXT,
            nombre_questions INTEGER DEFAULT 50,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
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

# ========== SÉCURITÉ: SHA256 PASSWORD HASHING ==========
def hash_password(password):
    """Hasher password avec SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_stored):
    """Vérifier password avec SHA256"""
    return hashlib.sha256(password.encode()).hexdigest() == hash_stored

# ========== SÉCURITÉ: RATE LIMITING ==========
def check_rate_limit(email, max_attempts=5, window_minutes=15):
    """Vérifier rate limiting"""
    cutoff_time = (datetime.now() - timedelta(minutes=window_minutes)).isoformat()
    
    failed = db.fetch_all(
        'SELECT * FROM failed_logins WHERE email = ? AND attempt_time > ?',
        (email, cutoff_time)
    )
    
    if len(failed) >= max_attempts:
        return False, f"⏳ Trop de tentatives. Attendez {window_minutes} min."
    
    return True, None

def record_failed_login(email):
    """Enregistrer une tentative échouée"""
    db.query('INSERT INTO failed_logins (email, ip_address) VALUES (?, ?)',
            (email, "unknown"))

def clear_failed_logins(email):
    """Effacer les tentatives échouées"""
    db.query('DELETE FROM failed_logins WHERE email = ?', (email,))

# ========== SÉCURITÉ: LOGS D'AUDIT ==========
def audit_log(user_id, action, details=""):
    """Enregistrer une action"""
    db.query(
        'INSERT INTO audit_logs (utilisateur_id, action, details, ip_address, timestamp) VALUES (?, ?, ?, ?, ?)',
        (user_id, action, details, "unknown", datetime.now().isoformat())
    )

# ========== SÉCURITÉ: SESSIONS ==========
def create_session(user_id):
    """Créer une session"""
    token = hashlib.sha256(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()
    
    user = db.fetch_one('SELECT session_duration_minutes FROM utilisateurs WHERE id = ?', (user_id,))
    expires_at = (datetime.now() + timedelta(minutes=user['session_duration_minutes'])).isoformat()
    
    db.query(
        'INSERT INTO sessions (utilisateur_id, token, ip_address, expires_at) VALUES (?, ?, ?, ?)',
        (user_id, token, "unknown", expires_at)
    )
    
    audit_log(user_id, "LOGIN", "Session créée")
    return token

def validate_session(token):
    """Valider une session"""
    session = db.fetch_one('SELECT * FROM sessions WHERE token = ?', (token,))
    
    if not session:
        return None
    
    if datetime.fromisoformat(session['expires_at']) < datetime.now():
        db.query('DELETE FROM sessions WHERE id = ?', (session['id'],))
        return None
    
    return session

def revoke_session(token):
    """Révoquer une session"""
    db.query('DELETE FROM sessions WHERE token = ?', (token,))

def revoke_user_sessions(user_id):
    """Révoquer TOUTES les sessions d'un utilisateur"""
    db.query('DELETE FROM sessions WHERE utilisateur_id = ?', (user_id,))

# ========== SÉCURITÉ: VALIDATION ==========
def is_valid_email(email):
    """Valider email"""
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def sanitize_input(text):
    """Nettoyer input"""
    dangerous_chars = ['<', '>', '"', "'", '{', '}', '&', '%']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text.strip()

# ========== FONCTIONS UTILITAIRES ==========
def add_user(nom, prenom, email, username, password):
    """Ajouter utilisateur"""
    try:
        password_hash = hash_password(password)
        db.query(
            'INSERT INTO utilisateurs (nom, prenom, email, username, password_hash, role) VALUES (?, ?, ?, ?, ?, ?)',
            (sanitize_input(nom), sanitize_input(prenom), email.lower(), sanitize_input(username), password_hash, 'apprenant')
        )
        user = db.fetch_one('SELECT id FROM utilisateurs WHERE email = ?', (email.lower(),))
        audit_log(user['id'], "REGISTRATION", "Inscription")
        return True
    except:
        return False

def get_user_by_email(email):
    """Récupérer utilisateur par email"""
    return db.fetch_one('SELECT * FROM utilisateurs WHERE email = ?', (email.lower(),))

def toggle_user_status(user_id):
    """Basculer status"""
    user = db.fetch_one('SELECT status FROM utilisateurs WHERE id = ?', (user_id,))
    new_status = 'bloqué' if user['status'] == 'actif' else 'actif'
    db.query('UPDATE utilisateurs SET status = ? WHERE id = ?', (new_status, user_id))
    
    if new_status == 'bloqué':
        revoke_user_sessions(user_id)

def set_session_duration(user_id, duration_minutes):
    """Définir durée de session"""
    if duration_minutes < 5 or duration_minutes > 1440:
        return False
    db.query('UPDATE utilisateurs SET session_duration_minutes = ? WHERE id = ?', 
            (duration_minutes, user_id))
    audit_log(None, "SESSION_CONFIG", f"Durée = {duration_minutes}min pour user {user_id}")
    return True

def get_all_users():
    """Récupérer tous les apprenants"""
    return db.fetch_all('SELECT * FROM utilisateurs WHERE role = "apprenant" ORDER BY date_creation DESC')

def add_series(nom, description, nombre_questions=50):
    """Ajouter une série"""
    try:
        db.query('INSERT INTO series (nom, description, nombre_questions) VALUES (?, ?, ?)',
                (sanitize_input(nom), sanitize_input(description), nombre_questions))
        return True
    except:
        return False

def get_all_series():
    """Récupérer toutes les séries"""
    return db.fetch_all('SELECT * FROM series ORDER BY date_creation DESC')

def get_quiz_by_series(series_id):
    """Récupérer quiz d'une série"""
    return db.fetch_all('SELECT * FROM quiz WHERE series_id = ? ORDER BY ordre', (series_id,))

def add_quiz_to_series(series_id, question, opt_a, opt_b, opt_c, opt_d, reponses, explication):
    """Ajouter un quiz"""
    db.query(
        'INSERT INTO quiz (series_id, question, option_a, option_b, option_c, option_d, reponses_correctes, explication, ordre) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (series_id, sanitize_input(question), sanitize_input(opt_a), sanitize_input(opt_b), 
         sanitize_input(opt_c), sanitize_input(opt_d), reponses, sanitize_input(explication), 0)
    )

def save_series_result(user_id, series_id, score, total):
    """Sauvegarder résultat série"""
    pourcentage = (score / total * 100) if total > 0 else 0
    db.query(
        'INSERT INTO resultats (utilisateur_id, series_id, score, total, pourcentage) VALUES (?, ?, ?, ?, ?)',
        (user_id, series_id, score, total, pourcentage)
    )
    audit_log(user_id, "SERIES_COMPLETED", f"Score {score}/{total}")

def get_audit_logs(limit=100):
    """Récupérer logs d'audit"""
    return db.fetch_all('SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?', (limit,))

# ========== CSS ==========
st.markdown("""
<style>
    * { font-family: 'Segoe UI', sans-serif; }
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
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "session_token" not in st.session_state:
    st.session_state.session_token = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "accueil"
if "admin_tab" not in st.session_state:
    st.session_state.admin_tab = "dashboard"

# ========== PAGE AUTHENTIFICATION ==========
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="header-title">
            <h1>🎓 Campus Réussite</h1>
            <p>Plateforme Sécurisée - Termux Compatible</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with tab1:
            st.markdown("### Connexion")
            
            email = st.text_input("Email", key="login_email")
            pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
            
            if st.button("Se Connecter", use_container_width=True, type="primary"):
                # Vérifier admin d'abord
                try:
                    admins = st.secrets.get("admins", {})
                    if email.lower() in admins and admins[email.lower()] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.user = {'nom': 'Admin', 'prenom': 'Campus', 'email': email.lower(), 'role': 'admin', 'id': 0}
                        st.session_state.is_admin = True
                        audit_log(0, "ADMIN_LOGIN", "Admin connecté")
                        st.rerun()
                except:
                    pass
                
                # Vérifier apprenant
                allowed, error_msg = check_rate_limit(email.lower())
                if not allowed:
                    st.error(error_msg)
                else:
                    user = get_user_by_email(email.lower())
                    
                    if user and verify_password(pwd, user['password_hash']):
                        if user['status'] == 'bloqué':
                            st.error("❌ Votre compte a été bloqué")
                            record_failed_login(email.lower())
                        else:
                            clear_failed_logins(email.lower())
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.session_state.session_token = create_session(user['id'])
                            st.session_state.is_admin = False
                            st.rerun()
                    else:
                        st.error("❌ Email ou mot de passe incorrect")
                        record_failed_login(email.lower())
        
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
                elif len(password) < 6:
                    st.error("❌ Min 6 caractères")
                elif password != pwd_confirm:
                    st.error("❌ Mots de passe différents")
                elif get_user_by_email(email.lower()):
                    st.error("❌ Email déjà utilisé")
                elif add_user(nom, prenom, email.lower(), username, password):
                    st.success("✅ Compte créé!")
                    user = get_user_by_email(email.lower())
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.session_token = create_session(user['id'])
                    st.session_state.is_admin = False
                    st.rerun()
                else:
                    st.error("❌ Erreur")

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
    
    # SIDEBAR
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
        else:
            st.markdown("### 🔐 Admin Panel")
            if st.button("🔧 Accès Admin"):
                st.session_state.is_admin = True
                st.rerun()
        
        st.divider()
        if st.button("🚪 Déconnexion"):
            if st.session_state.session_token:
                revoke_session(st.session_state.session_token)
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.is_admin = False
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
        
        # ACCUEIL
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
        
        # SÉRIES
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
        
        # RÉSULTATS
        elif st.session_state.current_page == "resultats":
            st.markdown("### 📊 Résultats")
            results = db.fetch_all('SELECT * FROM resultats WHERE utilisateur_id = ? ORDER BY date_completion DESC', (user['id'],))
            
            if results:
                df = pd.DataFrame([{
                    'Série': db.fetch_one('SELECT nom FROM series WHERE id = ?', (r['series_id'],))['nom'],
                    'Score': f"{r['score']}/{r['total']}",
                    '%': f"{r['pourcentage']:.0f}%",
                    'Date': r['date_completion'][:10]
                } for r in results])
                st.dataframe(df, use_container_width=True, hide_index=True)
        
        # FEEDBACK
        elif st.session_state.current_page == "feedback":
            st.markdown("### 💬 Feedback")
            
            with st.form("f"):
                titre = st.text_input("Titre")
                msg_type = st.selectbox("Type", ["Suggestion", "Problème", "Autre"])
                message = st.text_area("Message")
                
                if st.form_submit_button("Envoyer", use_container_width=True):
                    if titre and message:
                        db.query(
                            'INSERT INTO feedback (email, titre, message, type) VALUES (?, ?, ?, ?)',
                            (user['email'], sanitize_input(titre), sanitize_input(message), msg_type)
                        )
                        audit_log(user['id'], "FEEDBACK_SENT", titre)
                        st.success("✅ Feedback enregistré!")
        
        # QUIZ SÉRIE
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
                    st.error("❌ Répondez à TOUTES les questions!")
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
                        is_ok = set(your) == set(correct)
                        
                        with st.expander(f"Q{idx+1}: {quiz['question']}"):
                            st.markdown(f"**Votre réponse:** {', '.join(your) if your else 'Non répondue'}")
                            st.markdown(f"**Correcte:** {', '.join(correct)}")
                            if is_ok:
                                st.success("✅ Correct!")
                            else:
                                st.error("❌ Incorrect")
                            st.markdown(f"💡 {quiz['explication']}")
                    
                    st.divider()
                    if st.button("🏠 Retour"):
                        st.session_state.current_page = "accueil"
                        if f"answers_{series_id}" in st.session_state:
                            del st.session_state[f"answers_{series_id}"]
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
            if st.button("👥 Apprenants", use_container_width=True):
                st.session_state.admin_tab = "users"
                st.rerun()
        with col4:
            if st.button("📋 Audit", use_container_width=True):
                st.session_state.admin_tab = "audit"
                st.rerun()
        with col5:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.admin_tab = "feedback"
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
                total = sum(len(get_quiz_by_series(s['id'])) for s in get_all_series())
                st.markdown(f'<div class="stat-box"><div class="stat-number">{total}</div><div class="stat-label">Quizzes</div></div>', unsafe_allow_html=True)
            with col4:
                fb = db.fetch_all('SELECT * FROM feedback')
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(fb)}</div><div class="stat-label">Feedbacks</div></div>', unsafe_allow_html=True)
        
        # SÉRIES
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
        
        # APPRENANTS
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
                            revoke_user_sessions(u['id'])
                            st.info("Révoqué")
                    
                    st.divider()
        
        # AUDIT
        elif st.session_state.admin_tab == "audit":
            st.markdown("### 📋 Logs")
            
            logs = get_audit_logs(200)
            
            if logs:
                df = pd.DataFrame([{
                    'Action': log['action'],
                    'Détails': log['details'][:30] if log['details'] else "",
                    'Date': log['timestamp'][:19]
                } for log in logs])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
        
        # FEEDBACK
        elif st.session_state.admin_tab == "feedback":
            st.markdown("### 💬 Feedback")
            
            fb_list = db.fetch_all('SELECT * FROM feedback ORDER BY date_creation DESC')
            
            if fb_list:
                for fb in fb_list:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{fb['titre']}** | {fb['type']}")
                        st.markdown(f"📧 {fb['email']}")
                        st.markdown(f"{fb['message']}")
                    with col2:
                        st.caption(fb['date_creation'][:10])
                    st.divider()
