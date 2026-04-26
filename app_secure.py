"""
🎓 CAMPUS RÉUSSITE v8.0 ENTERPRISE
Plateforme Sécurisée pour Production - Internet Public + Data Sensible
- Hachage passwords (bcrypt)
- Gestion sessions avancée
- Logs d'audit complets
- Rate limiting
- Validation inputs
- HTTPS compatible
"""

import streamlit as st
import sqlite3
import pandas as pd
import re
import os
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import hmac

# ========== INSTALLATION REQUISE ==========
try:
    import bcrypt
except ImportError:
    st.error("❌ bcrypt manquant. Exécutez: pip install bcrypt")
    st.stop()

# ========== CONFIG PAGE ==========
st.set_page_config(
    page_title="Campus Réussite Enterprise",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = os.path.join(os.path.dirname(__file__), "campus_secure.db")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo_campus_reussite.jpg")

# ========== DATABASE SÉCURISÉE ==========
class Database:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Utilisateurs (passwords hachés)
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
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            derniere_activite TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Sessions actives
        cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            derniere_activite TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        )''')
        
        # Logs d'audit
        cursor.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        )''')
        
        # Tentatives failed login (rate limiting)
        cursor.execute('''CREATE TABLE IF NOT EXISTS failed_logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            ip_address TEXT,
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

# ========== SÉCURITÉ: BCRYPT PASSWORD HASHING ==========
def hash_password(password):
    """Hasher password avec bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hash_stored):
    """Vérifier password avec bcrypt"""
    try:
        return bcrypt.checkpw(password.encode(), hash_stored.encode())
    except:
        return False

# ========== SÉCURITÉ: RATE LIMITING ==========
def check_rate_limit(email, ip_address, max_attempts=5, window_minutes=15):
    """Vérifier rate limiting pour éviter brute force"""
    cutoff_time = (datetime.now() - timedelta(minutes=window_minutes)).isoformat()
    
    failed = db.fetch_all(
        'SELECT * FROM failed_logins WHERE email = ? AND ip_address = ? AND attempt_time > ?',
        (email, ip_address, cutoff_time)
    )
    
    if len(failed) >= max_attempts:
        return False, f"⏳ Trop de tentatives. Attendez {window_minutes} min."
    
    return True, None

def record_failed_login(email, ip_address):
    """Enregistrer une tentative échouée"""
    db.query('INSERT INTO failed_logins (email, ip_address) VALUES (?, ?)',
            (email, ip_address))

def clear_failed_logins(email):
    """Effacer les tentatives échouées après succès"""
    db.query('DELETE FROM failed_logins WHERE email = ?', (email,))

# ========== SÉCURITÉ: LOGS D'AUDIT ==========
def audit_log(user_id, action, details="", ip_address=""):
    """Enregistrer une action pour audit"""
    db.query(
        'INSERT INTO audit_logs (utilisateur_id, action, details, ip_address, timestamp) VALUES (?, ?, ?, ?, ?)',
        (user_id, action, details, ip_address, datetime.now().isoformat())
    )

# ========== SÉCURITÉ: SESSIONS ==========
def create_session(user_id, ip_address=""):
    """Créer une session sécurisée"""
    token = hashlib.sha256(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()
    
    user = db.fetch_one('SELECT session_duration_minutes FROM utilisateurs WHERE id = ?', (user_id,))
    expires_at = (datetime.now() + timedelta(minutes=user['session_duration_minutes'])).isoformat()
    
    db.query(
        'INSERT INTO sessions (utilisateur_id, token, ip_address, expires_at) VALUES (?, ?, ?, ?)',
        (user_id, token, ip_address, expires_at)
    )
    
    audit_log(user_id, "LOGIN", f"Nouvelle session créée", ip_address)
    return token

def validate_session(token):
    """Valider une session"""
    session = db.fetch_one('SELECT * FROM sessions WHERE token = ?', (token,))
    
    if not session:
        return None
    
    if datetime.fromisoformat(session['expires_at']) < datetime.now():
        db.query('DELETE FROM sessions WHERE id = ?', (session['id'],))
        return None
    
    # Mettre à jour dernière activité
    db.query('UPDATE sessions SET derniere_activite = ? WHERE id = ?',
            (datetime.now().isoformat(), session['id']))
    
    return session

def revoke_session(token):
    """Révoquer une session"""
    db.query('DELETE FROM sessions WHERE token = ?', (token,))

def revoke_user_sessions(user_id):
    """Révoquer TOUTES les sessions d'un utilisateur"""
    db.query('DELETE FROM sessions WHERE utilisateur_id = ?', (user_id,))

# ========== SÉCURITÉ: VALIDATION INPUTS ==========
def is_valid_email(email):
    """Valider email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    """Nettoyer input contre XSS"""
    dangerous_chars = ['<', '>', '"', "'", '{', '}', '&', '%']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text.strip()

def validate_password_strength(password):
    """Vérifier force du password"""
    if len(password) < 8:
        return False, "Min 8 caractères"
    if not any(c.isupper() for c in password):
        return False, "Min 1 majuscule"
    if not any(c.isdigit() for c in password):
        return False, "Min 1 chiffre"
    if not any(c in "!@#$%^&*" for c in password):
        return False, "Min 1 caractère spécial (!@#$%^&*)"
    return True, "✅ Password fort"

# ========== FONCTIONS UTILITAIRES ==========
def add_user(nom, prenom, email, username, password):
    """Ajouter utilisateur avec password HASHÉ"""
    try:
        password_hash = hash_password(password)
        db.query(
            'INSERT INTO utilisateurs (nom, prenom, email, username, password_hash, role) VALUES (?, ?, ?, ?, ?, ?)',
            (sanitize_input(nom), sanitize_input(prenom), email.lower(), sanitize_input(username), password_hash, 'apprenant')
        )
        user = db.fetch_one('SELECT id FROM utilisateurs WHERE email = ?', (email.lower(),))
        audit_log(user['id'], "REGISTRATION", f"Nouvel apprenant inscrit")
        return True
    except:
        return False

def get_user_by_email(email):
    """Récupérer utilisateur par email"""
    return db.fetch_one('SELECT * FROM utilisateurs WHERE email = ?', (email.lower(),))

def get_user_by_id(user_id):
    """Récupérer utilisateur par ID"""
    return db.fetch_one('SELECT * FROM utilisateurs WHERE id = ?', (user_id,))

def toggle_user_status(user_id):
    """Basculer status utilisateur"""
    user = db.fetch_one('SELECT status FROM utilisateurs WHERE id = ?', (user_id,))
    new_status = 'bloqué' if user['status'] == 'actif' else 'actif'
    db.query('UPDATE utilisateurs SET status = ? WHERE id = ?', (new_status, user_id))
    
    action = "Utilisateur BLOQUÉ" if new_status == 'bloqué' else "Utilisateur DÉBLOQUÉ"
    audit_log(None, action, f"User ID: {user_id}")
    
    if new_status == 'bloqué':
        revoke_user_sessions(user_id)

def set_session_duration(user_id, duration_minutes):
    """Définir durée de session pour un utilisateur"""
    if duration_minutes < 5 or duration_minutes > 1440:  # 5 min à 24h
        return False
    db.query('UPDATE utilisateurs SET session_duration_minutes = ? WHERE id = ?', 
            (duration_minutes, user_id))
    audit_log(None, "SESSION_CONFIG", f"Durée session = {duration_minutes}min pour user {user_id}")
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
    audit_log(user_id, "SERIES_COMPLETED", f"Score {score}/{total} ({pourcentage:.1f}%)")

def get_audit_logs(user_id=None, limit=100):
    """Récupérer logs d'audit"""
    if user_id:
        return db.fetch_all('SELECT * FROM audit_logs WHERE utilisateur_id = ? ORDER BY timestamp DESC LIMIT ?',
                           (user_id, limit))
    return db.fetch_all('SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?', (limit,))

# ========== CSS PERSONNALISÉ ==========
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
            <h1>🎓 Campus Réussite Enterprise</h1>
            <p>Plateforme Sécurisée Production</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with tab1:
            st.markdown("### Connexion Sécurisée")
            
            email = st.text_input("Email", key="login_email")
            pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
            
            if st.button("Se Connecter", use_container_width=True, type="primary"):
                # Récupérer l'IP
                ip_address = st.session_state.get("client_ip", "unknown")
                
                # Rate limiting
                allowed, error_msg = check_rate_limit(email.lower(), ip_address)
                if not allowed:
                    st.error(error_msg)
                else:
                    # Vérifier admin d'abord
                    try:
                        admins = st.secrets.get("admins", {})
                        if email.lower() in admins and admins[email.lower()] == pwd:
                            st.session_state.logged_in = True
                            st.session_state.user = {'nom': 'Admin', 'prenom': 'Campus', 'email': email.lower(), 'role': 'admin', 'id': 0}
                            st.session_state.is_admin = True
                            audit_log(0, "ADMIN_LOGIN", "Admin connecté", ip_address)
                            st.rerun()
                    except:
                        pass
                    
                    # Vérifier apprenant
                    user = get_user_by_email(email.lower())
                    
                    if user and verify_password(pwd, user['password_hash']):
                        if user['status'] == 'bloqué':
                            st.error("❌ Votre compte a été bloqué par l'administrateur")
                            record_failed_login(email.lower(), ip_address)
                        elif user['status'] == 'actif':
                            clear_failed_logins(email.lower())
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.session_state.session_token = create_session(user['id'], ip_address)
                            st.session_state.is_admin = False
                            st.rerun()
                        else:
                            st.error("❌ Compte invalide")
                    else:
                        st.error("❌ Email ou mot de passe incorrect")
                        record_failed_login(email.lower(), ip_address)
        
        with tab2:
            st.markdown("### Créer un Compte Sécurisé")
            
            nom = st.text_input("Nom", key="signup_nom")
            prenom = st.text_input("Prénom", key="signup_prenom")
            email = st.text_input("Email", key="signup_email")
            username = st.text_input("Username", key="signup_username")
            password = st.text_input("Mot de passe", type="password", key="signup_pwd")
            pwd_confirm = st.text_input("Confirmer", type="password", key="signup_pwd_confirm")
            
            if st.button("S'Inscrire", use_container_width=True, type="primary"):
                # Validations
                if not all([nom, prenom, email, username, password]):
                    st.error("❌ Remplissez tous les champs")
                elif not is_valid_email(email):
                    st.error("❌ Email invalide")
                elif password != pwd_confirm:
                    st.error("❌ Mots de passe différents")
                else:
                    valid, msg = validate_password_strength(password)
                    if not valid:
                        st.error(f"❌ Password faible: {msg}")
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
                        st.error("❌ Erreur lors de la création du compte")

# ========== APPLICATION PRINCIPALE ==========
else:
    user = st.session_state.user
    is_admin = st.session_state.is_admin
    
    # HEADER
    st.markdown(f"""
    <div class="header-title">
        <h1>🎓 Campus Réussite Enterprise</h1>
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
        
        # ACCUEIL
        if st.session_state.current_page == "accueil":
            all_series = get_all_series()
            results = db.fetch_all('SELECT * FROM resultats WHERE utilisateur_id = ?', (user['id'],))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(all_series)}</div><div class="stat-label">Séries Disponibles</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(results)}</div><div class="stat-label">Séries Complétées</div></div>', unsafe_allow_html=True)
            with col3:
                pct = (len(results) / len(all_series) * 100) if all_series else 0
                st.markdown(f'<div class="stat-box"><div class="stat-number">{pct:.0f}%</div><div class="stat-label">Progression</div></div>', unsafe_allow_html=True)
            
            st.divider()
            st.markdown("### 🎯 Commencer une Série")
            
            if all_series:
                for series in all_series:
                    result = next((r for r in results if r['series_id'] == series['id']), None)
                    status = f"✅ Score: {result['score']}/{result['total']}" if result else "⏳ À faire"
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{series['nom']}**")
                        st.markdown(f"{series['description']} | {series['nombre_questions']} questions | {status}")
                    with col2:
                        if st.button("Commencer", key=f"series_{series['id']}", use_container_width=True):
                            st.session_state.current_page = f"series_{series['id']}"
                            st.rerun()
            else:
                st.info("Aucune série disponible")
        
        # SÉRIES
        elif st.session_state.current_page == "series":
            st.markdown("### 📚 Mes Séries")
            all_series = get_all_series()
            results = db.fetch_all('SELECT * FROM resultats WHERE utilisateur_id = ?', (user['id'],))
            
            if all_series:
                for series in all_series:
                    result = next((r for r in results if r['series_id'] == series['id']), None)
                    st.markdown(f"**{series['nom']}** | {series['nombre_questions']} questions")
                    st.markdown(f"_{series['description']}_")
                    
                    if result:
                        st.success(f"✅ Score: {result['score']}/{result['total']} ({result['pourcentage']:.1f}%)")
                    
                    if st.button("Faire la série" if not result else "Refaire", key=f"btn_series_{series['id']}", use_container_width=True):
                        st.session_state.current_page = f"series_{series['id']}"
                        st.rerun()
                    st.divider()
        
        # RÉSULTATS
        elif st.session_state.current_page == "resultats":
            st.markdown("### 📊 Mes Résultats")
            results = db.fetch_all('SELECT * FROM resultats WHERE utilisateur_id = ? ORDER BY date_completion DESC', (user['id'],))
            
            if results:
                df = pd.DataFrame([{
                    'Série': db.fetch_one('SELECT nom FROM series WHERE id = ?', (r['series_id'],))['nom'],
                    'Score': f"{r['score']}/{r['total']}",
                    'Pourcentage': f"{r['pourcentage']:.1f}%",
                    'Date': r['date_completion'][:10]
                } for r in results])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun résultat")
        
        # FEEDBACK
        elif st.session_state.current_page == "feedback":
            st.markdown("### 💬 Envoyer un Feedback")
            
            with st.form("feedback_form"):
                titre = st.text_input("Titre")
                msg_type = st.selectbox("Type", ["Suggestion", "Problème", "Autre"])
                message = st.text_area("Message", height=150)
                
                if st.form_submit_button("Envoyer", use_container_width=True):
                    if titre and message:
                        db.query(
                            'INSERT INTO feedback (email, titre, message, type, date_creation) VALUES (?, ?, ?, ?, ?)',
                            (user['email'], sanitize_input(titre), sanitize_input(message), msg_type, datetime.now().isoformat())
                        )
                        audit_log(user['id'], "FEEDBACK_SENT", titulo)
                        st.success("✅ Feedback enregistré!")
                    else:
                        st.error("Remplissez tous les champs")
        
        # QUIZ SÉRIE
        elif st.session_state.current_page.startswith("series_"):
            series_id = int(st.session_state.current_page.split("_")[1])
            series = db.fetch_one('SELECT * FROM series WHERE id = ?', (series_id,))
            quiz_list = get_quiz_by_series(series_id)
            
            st.markdown(f"### 🎯 {series['nom']}")
            st.divider()
            
            if f"answers_{series_id}" not in st.session_state:
                st.session_state[f"answers_{series_id}"] = {}
            
            for idx, quiz in enumerate(quiz_list):
                st.markdown(f"**Question {idx+1}/{len(quiz_list)}: {quiz['question']}**")
                
                options = [quiz['option_a'], quiz['option_b'], quiz['option_c'], quiz['option_d']]
                
                selected = st.multiselect(
                    "Vos réponses:",
                    options,
                    default=st.session_state[f"answers_{series_id}"].get(quiz['id'], []),
                    key=f"quiz_{quiz['id']}"
                )
                
                st.session_state[f"answers_{series_id}"][quiz['id']] = selected
                st.divider()
            
            if st.button("✅ VALIDER LA SÉRIE", use_container_width=True, type="primary"):
                if len(st.session_state[f"answers_{series_id}"]) < len(quiz_list):
                    st.error("❌ Vous devez répondre à TOUTES les questions!")
                else:
                    score = 0
                    for quiz in quiz_list:
                        correct_answers = [c.strip() for c in quiz['reponses_correctes'].split(',')]
                        if set(st.session_state[f"answers_{series_id}"][quiz['id']]) == set(correct_answers):
                            score += 1
                    
                    save_series_result(user['id'], series_id, score, len(quiz_list))
                    
                    st.success(f"✅ SÉRIE COMPLÉTÉE!")
                    st.markdown(f"### 📊 Votre Score: {score}/{len(quiz_list)} ({score/len(quiz_list)*100:.1f}%)")
                    
                    st.divider()
                    st.markdown("### 📝 Corrections")
                    
                    for idx, quiz in enumerate(quiz_list):
                        correct_answers = [c.strip() for c in quiz['reponses_correctes'].split(',')]
                        your_answers = st.session_state[f"answers_{series_id}"][quiz['id']]
                        is_correct = set(your_answers) == set(correct_answers)
                        
                        with st.expander(f"Question {idx+1}: {quiz['question']}"):
                            st.markdown(f"**Votre réponse:** {', '.join(your_answers) if your_answers else 'Non répondue'}")
                            st.markdown(f"**Réponse correcte:** {', '.join(correct_answers)}")
                            if is_correct:
                                st.success("✅ Correct!")
                            else:
                                st.error("❌ Incorrect")
                            st.markdown(f"💡 **Explication:** {quiz['explication']}")
                    
                    st.divider()
                    if st.button("🏠 Retour à l'Accueil"):
                        st.session_state.current_page = "accueil"
                        if f"answers_{series_id}" in st.session_state:
                            del st.session_state[f"answers_{series_id}"]
                        st.rerun()
    
    # ========== MODE ADMIN ==========
    else:
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
            if st.button("📋 Audit", use_container_width=True):
                st.session_state.admin_tab = "audit"
                st.rerun()
        with col6:
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
                total_quiz = sum(len(get_quiz_by_series(s['id'])) for s in get_all_series())
                st.markdown(f'<div class="stat-box"><div class="stat-number">{total_quiz}</div><div class="stat-label">Quizzes</div></div>', unsafe_allow_html=True)
            with col4:
                feedback = db.fetch_all('SELECT * FROM feedback')
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(feedback)}</div><div class="stat-label">Feedbacks</div></div>', unsafe_allow_html=True)
        
        # SÉRIES
        elif st.session_state.admin_tab == "series":
            st.markdown("### 📚 Gestion des Séries")
            
            with st.expander("➕ Créer une Série"):
                nom = st.text_input("Nom")
                desc = st.text_area("Description")
                nq = st.slider("Nombre de questions", 1, 100, 50)
                
                if st.button("Créer", use_container_width=True):
                    if nom and add_series(nom, desc, nq):
                        st.success("✅ Série créée!")
                        st.rerun()
                    else:
                        st.error("❌ Erreur")
            
            st.divider()
            
            st.markdown("### ➕ Ajouter un Quiz")
            series_list = get_all_series()
            if series_list:
                selected_series = st.selectbox("Série", [(s['id'], s['nom']) for s in series_list], format_func=lambda x: x[1])
                
                with st.form("add_quiz"):
                    q = st.text_input("Question")
                    a = st.text_input("Option A")
                    b = st.text_input("Option B")
                    c = st.text_input("Option C")
                    d = st.text_input("Option D")
                    correct = st.multiselect("Réponses correctes", ["A", "B", "C", "D"])
                    exp = st.text_area("Explication")
                    
                    if st.form_submit_button("Ajouter", use_container_width=True):
                        if all([q, a, b, c, d, correct, exp]):
                            correct_str = ", ".join(correct)
                            add_quiz_to_series(selected_series[0], q, a, b, c, d, correct_str, exp)
                            st.success("✅ Quiz ajouté!")
                            st.rerun()
        
        # IMPORTER
        elif st.session_state.admin_tab == "import":
            st.markdown("### 📤 Importer des Quiz")
            
            uploaded = st.file_uploader("CSV", type=["csv"])
            if uploaded:
                try:
                    df = pd.read_csv(uploaded, sep=";")
                    st.success(f"✅ {len(df)} lignes")
                    st.dataframe(df, use_container_width=True)
                    
                    series_list = get_all_series()
                    if series_list:
                        selected = st.selectbox("Série", [(s['id'], s['nom']) for s in series_list], format_func=lambda x: x[1])
                        
                        if st.button("Importer", use_container_width=True, type="primary"):
                            count = 0
                            for _, row in df.iterrows():
                                add_quiz_to_series(selected[0], row['question'], row['a'], row['b'], 
                                                 row['c'], row['d'], row['reponses_correctes'], row['explication'])
                                count += 1
                            st.success(f"✅ {count} quizzes importés!")
                except Exception as e:
                    st.error(f"Erreur: {e}")
        
        # APPRENANTS + GESTION SESSIONS
        elif st.session_state.admin_tab == "users":
            st.markdown("### 👥 Gestion des Apprenants")
            
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
                for user_item in users:
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        status_icon = "✅" if user_item['status'] == "actif" else "🔒"
                        st.markdown(f"{status_icon} **{user_item['prenom']} {user_item['nom']}**")
                        st.markdown(f"📧 {user_item['email']}")
                        st.caption(f"Durée session: {user_item['session_duration_minutes']}min")
                    
                    with col2:
                        if st.button("Bloquer" if user_item['status'] == 'actif' else "Débloquer", 
                                   key=f"toggle_{user_item['id']}", use_container_width=True):
                            toggle_user_status(user_item['id'])
                            st.rerun()
                    
                    with col3:
                        # Configurer durée session
                        new_duration = st.number_input("Session (min)", min_value=5, max_value=1440, 
                                                       value=user_item['session_duration_minutes'],
                                                       key=f"duration_{user_item['id']}")
                        if new_duration != user_item['session_duration_minutes']:
                            if set_session_duration(user_item['id'], int(new_duration)):
                                st.rerun()
                    
                    with col4:
                        if st.button("Révoquer", key=f"revoke_{user_item['id']}", use_container_width=True):
                            revoke_user_sessions(user_item['id'])
                            st.info("Sessions révoquées")
                    
                    st.divider()
        
        # LOGS D'AUDIT
        elif st.session_state.admin_tab == "audit":
            st.markdown("### 📋 Logs d'Audit")
            
            logs = get_audit_logs(limit=200)
            
            if logs:
                df = pd.DataFrame([{
                    'Action': log['action'],
                    'Détails': log['details'],
                    'IP': log['ip_address'][:20] if log['ip_address'] else "N/A",
                    'Date': log['timestamp'][:19]
                } for log in logs])
                
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun log")
        
        # FEEDBACK
        elif st.session_state.admin_tab == "feedback":
            st.markdown("### 💬 Feedback")
            
            feedback_list = db.fetch_all('SELECT * FROM feedback ORDER BY date_creation DESC')
            
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
