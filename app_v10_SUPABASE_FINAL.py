"""
🎓 CAMPUS RÉUSSITE v13 — PREMIUM UI + RÉCUPÉRATION COMPTE + NOTATION STRICTE
✅ Fond d'image style Glassmorphism (naturel et premium)
✅ Récupération de compte (code à 6 chiffres affiché à l'écran)
✅ Notation stricte des QCM (toutes les bonnes, aucune mauvaise)
✅ Hash PBKDF2 + migration auto
✅ Permissions admin réelles
✅ Paywall Orange Money
"""

import streamlit as st
import pandas as pd
import json
import hashlib
import hmac
import time
import os
import base64
import random
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Campus Réussite",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== CSS PREMIUM ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    * { margin:0; padding:0; box-sizing:border-box; }
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    /* GLASSMORPHISM POUR LES CONTENEURS STREAMLIT */
    [data-testid="stForm"], .stTabs [data-baseweb="tab-list"], .stTabs [data-baseweb="tab-panel"] {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1) !important;
        border: 1px solid rgba(255,255,255,0.5) !important;
    }

    .header-main { 
        background: linear-gradient(135deg, rgba(102,126,234,0.95) 0%, rgba(118,75,162,0.95) 100%);
        color:white; padding:35px; border-radius:20px; margin-bottom:25px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.2); text-align:center;
        backdrop-filter: blur(10px);
    }
    .header-main h1 { font-size:2.5em; font-weight:700; margin-bottom:10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .header-main p { font-size:1.1em; opacity:0.95; }
    
    .card-quiz { 
        background: rgba(255,255,255,0.95); color:#1a1a1a; padding:25px; border-radius:18px; 
        margin:15px 0; transition: all 0.3s ease; box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.8); overflow:hidden;
    }
    .card-quiz:hover { transform: translateY(-8px); box-shadow: 0 15px 40px rgba(102,126,234,0.3); }
    .card-quiz-title { font-size:1.4em; font-weight:700; color:#667eea; margin:10px 0; }
    .card-quiz-desc { font-size:0.95em; color:#555; margin-bottom:15px; }
    .card-quiz-count { font-size:1.1em; font-weight:600; color:#764ba2; border-top:1px solid #eee; padding-top:10px; }
    
    .question-box { 
        background: rgba(255,255,255,0.95); padding:25px; border-radius:15px; margin:20px 0;
        border-left: 6px solid #667eea; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .question-number { font-size:0.85em; color:#667eea; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }
    .question-text { font-size:1.3em; color:#1a1a1a; font-weight:600; line-height:1.5; }
    
    .progress-container { margin:20px 0; padding:15px; background:rgba(255,255,255,0.95); border-radius:12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .progress-bar { width:100%; height:10px; background:#e0e0e0; border-radius:10px; overflow:hidden; margin-top:8px; }
    .progress-fill { height:100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); transition: width 0.4s ease; }
    
    .score-display { background: linear-gradient(135deg, #34d399 0%, #10b981 100%); color:white; padding:30px; border-radius:15px; text-align:center; margin:20px 0; box-shadow: 0 10px 30px rgba(52,211,153,0.3); }
    .score-display.orange { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    .score-display.red { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
    .score-big { font-size:3.5em; font-weight:700; margin:15px 0; }
    
    .stat-box { background: rgba(255,255,255,0.95); color:#1a1a1a; padding:20px; border-radius:15px; text-align:center; margin:10px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-top: 4px solid #667eea; }
    .stat-box-number { font-size:2.2em; font-weight:700; color:#667eea; margin:5px 0; }
    .stat-box-label { font-size:0.9em; color:#666; font-weight:600; }
    
    .paywall-om { background: linear-gradient(135deg,#ff7900,#ff9500); color:white; padding:25px; border-radius:15px; text-align:center; margin:15px 0; box-shadow: 0 10px 30px rgba(255,121,0,0.3); }
    .paywall-om-num { font-size:2em; font-weight:900; letter-spacing:2px; margin:10px 0; }
    
    .correction-box { background:white; padding:20px; border-radius:12px; margin:15px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# ========== DB CLASS ==========
import psycopg2
import psycopg2.extras
from psycopg2 import pool as pg_pool

def _show_db_error_page(etape, message, url_partielle=""):
    st.markdown(f"""
    <div style="background:#fff3cd;border:2px solid #ffc107;border-radius:15px;padding:30px;margin:20px 0;">
        <h2 style="color:#856404;">⚠️ Problème de Connexion Base de Données</h2>
        <p><b>Etape :</b> {etape}</p>
        <code>{message}</code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

@st.cache_resource
def get_pool(url: str):
    try:
        return pg_pool.ThreadedConnectionPool(
            minconn=1, maxconn=5, dsn=url, sslmode="require",
            connect_timeout=10, keepalives=1, keepalives_idle=30,
            keepalives_interval=10, keepalives_count=5,
        )
    except Exception as e:
        _show_db_error_page("Pool de connexions", str(e)[:200], url[:40])

class DB:
    def __init__(self):
        self._url = self._get_url()
        self._pool = get_pool(self._url)
        self.init()

    def _get_url(self):
        if "DATABASE_URL" not in st.secrets:
            _show_db_error_page("Lecture DATABASE_URL", "Clé introuvable dans Secrets.")
        url = st.secrets["DATABASE_URL"]
        if not url.startswith("postgresql"):
            _show_db_error_page("Format URL", "L'URL doit commencer par postgresql://")
        return self._encoder_url(url)

    def _encoder_url(self, url):
        from urllib.parse import quote, urlparse, urlunparse
        try:
            parsed = urlparse(url)
            if parsed.password:
                mdp = quote(parsed.password, safe="")
                netloc = parsed.netloc.replace(f":{parsed.password}@", f":{mdp}@")
                return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
        except: pass
        return url

    def _conn(self):
        return self._pool.getconn()

    def _release(self, conn):
        self._pool.putconn(conn)

    def init(self):
        conn = self._conn()
        try:
            c = conn.cursor()
            tables = [
                """CREATE TABLE IF NOT EXISTS utilisateurs (
                    id SERIAL PRIMARY KEY, nom TEXT, prenom TEXT,
                    email TEXT UNIQUE, password_hash TEXT,
                    role TEXT DEFAULT 'apprenant', status TEXT DEFAULT 'actif',
                    session_minutes INTEGER DEFAULT 120,
                    last_activity TIMESTAMP DEFAULT NOW(),
                    tentatives_connexion INTEGER DEFAULT 0,
                    bloque INTEGER DEFAULT 0, date_blocage TEXT, raison_blocage TEXT)""",
                """CREATE TABLE IF NOT EXISTS admins (
                    id SERIAL PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, nom TEXT, prenom TEXT,
                    niveau_permission TEXT DEFAULT 'secondaire', peut_supprimer_quiz INTEGER DEFAULT 0,
                    peut_ajouter_admin INTEGER DEFAULT 0, peut_bloquer_users INTEGER DEFAULT 0,
                    peut_supprimer_users INTEGER DEFAULT 0, peut_supprimer_admins INTEGER DEFAULT 0,
                    date_creation TIMESTAMP DEFAULT NOW(), status TEXT DEFAULT 'actif')""",
                "ALTER TABLE admins ADD COLUMN IF NOT EXISTS peut_gerer_paiements INTEGER DEFAULT 0",
                """CREATE TABLE IF NOT EXISTS series (
                    id SERIAL PRIMARY KEY, nom TEXT UNIQUE, description TEXT, nombre_questions INTEGER DEFAULT 0)""",
                "ALTER TABLE series ADD COLUMN IF NOT EXISTS image_data TEXT",
                """CREATE TABLE IF NOT EXISTS maintenance (
                    id SERIAL PRIMARY KEY, actif INTEGER DEFAULT 0, message TEXT DEFAULT '', updated_at TIMESTAMP DEFAULT NOW())""",
                """CREATE TABLE IF NOT EXISTS quiz (
                    id SERIAL PRIMARY KEY, series_id INTEGER, question TEXT, option_a TEXT, option_b TEXT,
                    option_c TEXT, option_d TEXT, reponses_correctes TEXT, explication TEXT)""",
                """CREATE TABLE IF NOT EXISTS resultats (
                    id SERIAL PRIMARY KEY, utilisateur_id INTEGER, series_id INTEGER, score INTEGER, total INTEGER,
                    pourcentage REAL, date_test TIMESTAMP DEFAULT NOW())""",
                """CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY, email TEXT, titre TEXT, message TEXT, type TEXT, date_feedback TIMESTAMP DEFAULT NOW())""",
                """CREATE TABLE IF NOT EXISTS parametres (
                    cle TEXT PRIMARY KEY, valeur TEXT, updated_at TIMESTAMP DEFAULT NOW())""",
                """CREATE TABLE IF NOT EXISTS offres (
                    id SERIAL PRIMARY KEY, nom TEXT, montant INTEGER, duree_jours INTEGER, actif INTEGER DEFAULT 1, ordre INTEGER DEFAULT 0)""",
                """CREATE TABLE IF NOT EXISTS abonnements (
                    id SERIAL PRIMARY KEY, utilisateur_id INTEGER, date_debut TIMESTAMP DEFAULT NOW(),
                    date_fin TIMESTAMP, type TEXT DEFAULT 'essai', statut TEXT DEFAULT 'actif', notes TEXT)""",
                """CREATE TABLE IF NOT EXISTS paiements (
                    id SERIAL PRIMARY KEY, utilisateur_id INTEGER, offre_id INTEGER, montant INTEGER,
                    reference TEXT, notes TEXT, statut TEXT DEFAULT 'en_attente',
                    date_soumission TIMESTAMP DEFAULT NOW(), date_validation TIMESTAMP, valide_par TEXT)""",
                """CREATE TABLE IF NOT EXISTS reset_codes (
                    id SERIAL PRIMARY KEY, email TEXT, code TEXT, expires_at TIMESTAMP, used INTEGER DEFAULT 0)"""
            ]
            for sql in tables: c.execute(sql)

            c.execute("SELECT 1 FROM parametres WHERE cle='orange_money_numero'")
            if not c.fetchone():
                for k, v in [('orange_money_numero','À CONFIGURER'), ('whatsapp_numero','+226 XX XX XX XX'), ('duree_essai_jours','14')]:
                    c.execute("INSERT INTO parametres (cle,valeur) VALUES (%s,%s)", (k, v))

            c.execute("SELECT 1 FROM offres LIMIT 1")
            if not c.fetchone():
                for nom, montant, duree in [('1 mois', 2000, 30), ('3 mois', 5000, 90), ('6 mois', 9000, 180)]:
                    c.execute("INSERT INTO offres (nom,montant,duree_jours) VALUES (%s,%s,%s)", (nom, montant, duree))

            c.execute("""INSERT INTO abonnements (utilisateur_id, date_fin, type)
                         SELECT u.id, NOW() + INTERVAL '14 days', 'essai' FROM utilisateurs u
                         LEFT JOIN abonnements a ON a.utilisateur_id = u.id WHERE a.id IS NULL""")
            conn.commit()
        except Exception as e:
            conn.rollback()
            _show_db_error_page("Création des tables", str(e)[:200])
        finally:
            self._release(conn)

    def q(self, sql, p=()):
        conn = self._conn()
        try:
            c = conn.cursor(); c.execute(sql.replace("?","%s"), p); conn.commit(); return True
        except Exception as e:
            conn.rollback(); st.warning(f"Erreur BD: {str(e)[:150]}"); return False
        finally: self._release(conn)

    def f1(self, sql, p=()):
        conn = self._conn()
        try:
            c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            c.execute(sql.replace("?","%s"), p); r = c.fetchone(); return dict(r) if r else None
        except: return None
        finally: self._release(conn)

    def fa(self, sql, p=()):
        conn = self._conn()
        try:
            c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            c.execute(sql.replace("?","%s"), p); rows = c.fetchall(); return [dict(r) for r in rows] if rows else []
        except: return []
        finally: self._release(conn)

db = DB()

# ========== HASHING ==========
def hash_pwd(p):
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', p.encode(), salt, 200_000)
    return f"pbkdf2$200000${salt.hex()}${dk.hex()}"

def verify_pwd(p, h):
    if not h: return False
    if len(h) == 64 and all(c in '0123456789abcdef' for c in h):
        return hmac.compare_digest(hashlib.sha256((p + "salt2024").encode()).hexdigest(), h)
    if h.startswith("pbkdf2$"):
        try:
            _, iter_s, salt_hex, hash_hex = h.split("$")
            return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256', p.encode(), bytes.fromhex(salt_hex), int(iter_s)), bytes.fromhex(hash_hex))
        except: return False
    return False

def _upgrade_hash(user_id, password, table='utilisateurs'):
    row = db.f1(f'SELECT password_hash FROM {table} WHERE id=%s', (user_id,))
    if row and row['password_hash'] and not row['password_hash'].startswith("pbkdf2$"):
        db.q(f'UPDATE {table} SET password_hash=%s WHERE id=%s', (hash_pwd(password), user_id))

# ========== HELPERS ==========
def safe(obj, key, defaut="N/A"):
    if obj is None: return defaut
    try:
        val = obj.get(key, defaut) if isinstance(obj, dict) else getattr(obj, key, defaut)
        return val if val is not None else defaut
    except: return defaut

def get_perms():
    all_true = {k: True for k in ['principal','supprimer_quiz','ajouter_admin','bloquer_users','supprimer_users','supprimer_admins','gerer_paiements','gerer_parametres']}
    if st.session_state.user.get('id', 0) == 0: return all_true
    adm = db.f1("SELECT * FROM admins WHERE email=%s", (st.session_state.user.get('email',''),))
    if not adm: return {k: False for k in all_true}
    return {
        'principal': adm.get('niveau_permission') == 'principal',
        'supprimer_quiz': adm.get('peut_supprimer_quiz', 0) == 1,
        'ajouter_admin': adm.get('peut_ajouter_admin', 0) == 1,
        'bloquer_users': adm.get('peut_bloquer_users', 0) == 1,
        'supprimer_users': adm.get('peut_supprimer_users', 0) == 1,
        'supprimer_admins': adm.get('peut_supprimer_admins', 0) == 1,
        'gerer_paiements': adm.get('peut_gerer_paiements', 0) == 1 or adm.get('niveau_permission') == 'principal',
        'gerer_parametres': adm.get('niveau_permission') == 'principal',
    }

def a_acces_quiz(user_id):
    return db.f1('SELECT id FROM abonnements WHERE utilisateur_id=%s AND date_fin > NOW() LIMIT 1', (user_id,)) is not None

def jours_restants(user_id):
    r = db.f1('SELECT EXTRACT(DAY FROM (date_fin - NOW()))::int AS jours FROM abonnements WHERE utilisateur_id=%s AND date_fin > NOW() ORDER BY date_fin DESC LIMIT 1', (user_id,))
    return r['jours'] if r and r['jours'] is not None else 0

def creer_essai(user_id):
    duree = db.f1("SELECT valeur FROM parametres WHERE cle='duree_essai_jours'")
    jours = int(duree['valeur']) if duree and duree['valeur'] else 14
    db.q("INSERT INTO abonnements (utilisateur_id, date_fin, type) VALUES (%s, NOW() + INTERVAL '1 day' * %s, 'essai')", (user_id, jours))

def prolonger_abo(user_id, jours):
    r = db.f1('SELECT date_fin FROM abonnements WHERE utilisateur_id=%s AND date_fin > NOW() ORDER BY date_fin DESC LIMIT 1', (user_id,))
    if r and r['date_fin']:
        db.q("INSERT INTO abonnements (utilisateur_id, date_fin, type, statut) VALUES (%s, (SELECT date_fin FROM abonnements WHERE utilisateur_id=%s AND date_fin > NOW() ORDER BY date_fin DESC LIMIT 1) + INTERVAL '1 day' * %s, 'payant', 'actif')", (user_id, user_id, jours))
    else:
        db.q("INSERT INTO abonnements (utilisateur_id, date_fin, type, statut) VALUES (%s, NOW() + INTERVAL '1 day' * %s, 'payant', 'actif')", (user_id, jours))

# ========== SESSION & IMAGES ==========
def check_session_timeout():
    if not st.session_state.logged_in or not st.session_state.user or st.session_state.is_admin: return
    try:
        user = db.f1('SELECT * FROM utilisateurs WHERE id=?', (st.session_state.user['id'],))
        if not user or not user.get('last_activity'): return
        last = user['last_activity']
        dt = last.replace(tzinfo=None) if isinstance(last, datetime) else datetime.strptime(last.split('.')[0].replace('T',' '), '%Y-%m-%d %H:%M:%S') if isinstance(last, str) else datetime.now()
        timeout = user.get('session_minutes', 120) or 120
        if (datetime.now() - dt).total_seconds() / 60 > timeout:
            st.session_state.logged_in = False; st.session_state.user = None
            st.warning("⏰ Session expirée!"); st.rerun()
    except: pass

def update_activity():
    if st.session_state.logged_in and st.session_state.user and not st.session_state.is_admin:
        if time.time() - st.session_state.get('_last_push', 0) > 30:
            db.q('UPDATE utilisateurs SET last_activity=NOW() WHERE id=?', (st.session_state.user['id'],))
            st.session_state._last_push = time.time()

@st.cache_data
def _get_bg_b64():
    # Liste élargie de noms pour trouver l'image
    for fname in ["background.png", "background.jpg", "fond.png", "fond.jpg", "campus.png", "campus.jpg", "logo.png", "affiche.png", "affiche.jpg"]:
        if os.path.exists(fname):
            try:
                with open(fname, "rb") as f:
                    data = base64.b64encode(f.read()).decode()
                mime = "jpeg" if fname.lower().endswith(('jpg','jpeg')) else "png"
                return data, mime
            except: pass
    return None, None

def inject_background():
    data, mime = _get_bg_b64()
    if not data: return
    st.markdown(f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {{
        background-image: 
            linear-gradient(135deg, rgba(245,247,250,0.75) 0%, rgba(195,207,226,0.75) 100%),
            url('data:image/{mime};base64,{data}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{ background: transparent; }}
    </style>
    """, unsafe_allow_html=True)

def process_series_image(uploaded_file, max_size=(800, 800)):
    try:
        from PIL import Image
        import io
        img = Image.open(uploaded_file)
        img.thumbnail(max_size, Image.LANCZOS)
        if img.mode in ('RGBA', 'P', 'LA'): img = img.convert('RGB')
        buf = io.BytesIO(); img.save(buf, format='JPEG', quality=85, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except: return None

def display_logo():
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2: st.image("logo.png", width=150)

def get_score_color(pct):
    if pct >= 80: return "green", "🎉 Excellent!", "#34d399"
    elif pct >= 60: return "orange", "👍 Bien joué!", "#f59e0b"
    else: return "red", "💪 Continuez!", "#ef4444"

# ========== CORRECTION STRICTE ==========
def display_correction(quizzes, quiz_answers, serie):
    score = 0
    details = []
    for q in quizzes:
        user_raw = quiz_answers.get(q['id']) or []
        user_list = [user_raw] if isinstance(user_raw, str) else list(user_raw)
        correct_list = [c.strip() for c in q['reponses_correctes'].split(",")]
        
        # NOTATION STRICTE: Ensembles identiques (ni plus, ni moins)
        is_correct = set(user_list) == set(correct_list)
        
        if is_correct: score += 1
        details.append({
            'question': q['question'], 'user_list': user_list, 'correct_answers': correct_list,
            'explication': q['explication'], 'is_correct': is_correct,
            'options_dict': {'A': q['option_a'], 'B': q['option_b'], 'C': q['option_c'], 'D': q['option_d']}
        })

    pct = (score / len(quizzes)) * 100 if quizzes else 0
    _, msg, _ = get_score_color(pct)

    st.markdown(f"""
    <div class="header-main">
        <h2>📋 Correction Détaillée</h2>
        <p>{serie['nom']}</p>
    </div>
    <div class="score-display {'orange' if 60<=pct<80 else 'red' if pct<60 else ''}">
        <h2>✨ Résultat</h2>
        <div class="score-big">{score}/{len(quizzes)}</div>
        <div style="font-size:2em;font-weight:700;">{pct:.1f}%</div>
        <div style="font-size:1.2em;margin-top:10px;">{msg}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#1a1a1a;margin:30px 0 20px 0;'>🔍 Détail des réponses</h3>", unsafe_allow_html=True)

    for idx, d in enumerate(details, 1):
        border = "#10b981" if d['is_correct'] else "#ef4444"
        badge = "✅ CORRECT" if d['is_correct'] else "❌ INCORRECT"
        bg_badge = "#d1fae5" if d['is_correct'] else "#fee2e2"
        color_badge = "#065f46" if d['is_correct'] else "#7f1d1d"
        
        st.markdown(f"""
        <div class="correction-box" style="border-left:6px solid {border};">
            <div style="display:flex;justify-content:space-between;margin-bottom:15px;">
                <span style="font-weight:700;color:#667eea;">Question {idx}/{len(details)}</span>
                <span style="background:{bg_badge};color:{color_badge};padding:4px 12px;border-radius:20px;font-weight:700;font-size:0.85em;">{badge}</span>
            </div>
            <div style="font-size:1.2em;font-weight:600;margin-bottom:15px;">{d['question']}</div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div style='color:#667eea;font-weight:700;font-size:0.9em;margin-bottom:5px;'>👤 Votre choix</div>", unsafe_allow_html=True)
            if d['user_list']:
                for a in sorted(d['user_list']):
                    st.markdown(f"<div style='background:#f8f9fa;padding:10px;border-radius:6px;border-left:4px solid {border};margin-bottom:5px;'><b>{a})</b> {d['options_dict'].get(a,'')}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='background:#fff5f5;padding:10px;border-radius:6px;color:#ef4444;font-weight:bold;'>Non répondu</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div style='color:#10b981;font-weight:700;font-size:0.9em;margin-bottom:5px;'>✅ Bonne(s) réponse(s)</div>", unsafe_allow_html=True)
            for a in d['correct_answers']:
                st.markdown(f"<div style='background:#f0fdf4;padding:10px;border-radius:6px;border-left:4px solid #10b981;margin-bottom:5px;'><b>{a})</b> {d['options_dict'].get(a,'')}</div>", unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background:#fef3c7;padding:15px;border-radius:8px;margin-top:15px;border-left:4px solid #f59e0b;">
                <div style="font-weight:700;color:#92400e;font-size:0.9em;margin-bottom:5px;">💡 Explication</div>
                <div style="color:#78350f;font-size:0.95em;">{d['explication']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return score, pct

# ========== INIT STATE ==========
defaults = {
    "logged_in": False, "is_admin": False, "user": None, "page": "home",
    "quiz_answers": {}, "quiz_submitted": False, "editing_quiz_id": None,
    "current_series_id": None, "current_quizzes": [], 
    "register_form_key": 0, "quiz_form_key": 0, "serie_form_key": 0, "admin_form_key": 0,
    "_last_push": 0, "reset_step": 0, "reset_email": "", "reset_code_gen": ""
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

check_session_timeout()
update_activity()

def afficher_banniere_maintenance():
    try:
        m = db.f1("SELECT * FROM maintenance ORDER BY id DESC LIMIT 1")
        if m and m.get('actif', 0) == 1 and m.get('message', '').strip():
            st.markdown(f"<div style='background:linear-gradient(135deg,#f39c12,#e67e22);color:white;padding:15px;border-radius:12px;margin-bottom:20px;text-align:center;font-weight:700;'>🔧 Maintenance : {m['message']}</div>", unsafe_allow_html=True)
    except: pass

afficher_banniere_maintenance()
inject_background()

# ========== PAYWALL ==========
def afficher_paywall(uid, prenom):
    st.markdown(f"""
    <div class="header-main" style="background:linear-gradient(135deg,#ef4444,#dc2626);">
        <h1>⏰ Essai terminé</h1>
        <p>{prenom}, abonnez-vous pour continuer</p>
    </div>
    """, unsafe_allow_html=True)

    om = db.f1("SELECT valeur FROM parametres WHERE cle='orange_money_numero'") or {'valeur':'À CONFIGURER'}
    wa = db.f1("SELECT valeur FROM parametres WHERE cle='whatsapp_numero'") or {'valeur':'N/A'}
    offres = db.fa("SELECT * FROM offres WHERE actif=1 ORDER BY montant")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="paywall-om">
            <div style="font-size:0.9em;">Envoyez le montant au</div>
            <div class="paywall-om-num">{om['valeur']}</div>
            <div style="font-size:0.9em;">Orange Money</div>
        </div>
        <p><b>📋 Comment payer :</b></p>
        <ol style="font-size:0.95em;margin-left:20px;">
            <li>Faites le dépôt Orange Money</li>
            <li>Prenez une capture d'écran</li>
            <li>Envoyez sur WhatsApp : <b>{wa['valeur']}</b></li>
            <li>Remplissez le formulaire avec la référence</li>
        </ol>
        """, unsafe_allow_html=True)

    with col2:
        if not offres: return
        offre = st.selectbox("Votre offre", [(o['id'], f"{o['nom']} — {o['montant']} FCFA ({o['duree_jours']}j)") for o in offres], format_func=lambda x: x[1])
        
        attente = db.f1("SELECT * FROM paiements WHERE utilisateur_id=%s AND statut='en_attente' LIMIT 1", (uid,))
        if attente:
            st.warning(f"⏳ Paiement de {attente['montant']} FCFA en attente de validation.")
        else:
            with st.form("pay_form"):
                ref = st.text_input("🔢 Référence de transaction *")
                notes = st.text_area("📝 Notes (optionnel)")
                if st.form_submit_button("📤 Envoyer", use_container_width=True, type="primary"):
                    if ref.strip():
                        info = next(o for o in offres if o['id'] == offre[0])
                        db.q("INSERT INTO paiements (utilisateur_id, offre_id, montant, reference, notes) VALUES (?,?,?,?,?)", (uid, info['id'], info['montant'], ref.strip(), notes))
                        st.success("✅ Paiement soumis !"); st.balloons(); st.rerun()
                    else: st.error("Référence obligatoire")

# ========== LOGIN PAGE AVEC RÉCUPÉRATION ==========
if not st.session_state.logged_in:
    display_logo()
    st.markdown("""
    <div class="header-main">
        <h1>🎓 Campus Réussite</h1>
        <p>Ose Réussir !</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])

        with tab1:
            st.subheader("Connexion")
            email = st.text_input("📧 Email", key="login_email")
            pwd = st.text_input("🔑 Mot de passe", type="password", key="login_pwd")
            
            if st.button("✨ Se Connecter", use_container_width=True, type="primary"):
                # Admin Secrets
                try:
                    admins_secrets = st.secrets.get("admins", {})
                    if email.lower() in admins_secrets and admins_secrets[email.lower()] == pwd:
                        st.session_state.logged_in, st.session_state.is_admin = True, True
                        st.session_state.user = {'nom':'Principal','prenom':'Admin','email':email.lower(),'id':0}
                        st.rerun()
                except: pass
                
                # Admin DB
                admin = db.f1("SELECT * FROM admins WHERE email=? AND status='actif'", (email.lower(),))
                if admin and verify_pwd(pwd, admin['password_hash']):
                    _upgrade_hash(admin['id'], pwd, 'admins')
                    st.session_state.logged_in, st.session_state.is_admin = True, True
                    st.session_state.user = {k:v for k,v in admin.items() if k!='password_hash'}
                    st.rerun()
                
                # User DB
                user = db.f1('SELECT * FROM utilisateurs WHERE email=?', (email.lower(),))
                if user:
                    if user.get('bloque', 0) == 1: st.error("🚫 Compte bloqué.")
                    elif user.get('tentatives_connexion', 0) >= 3: st.error("🚫 Compte bloqué après 3 tentatives.")
                    elif verify_pwd(pwd, user['password_hash']):
                        _upgrade_hash(user['id'], pwd)
                        db.q('UPDATE utilisateurs SET tentatives_connexion=0, last_activity=NOW() WHERE id=?', (user['id'],))
                        st.session_state.logged_in, st.session_state.is_admin = True, False
                        st.session_state.user = {k:v for k,v in user.items() if k!='password_hash'}
                        st.rerun()
                    else:
                        nt = user.get('tentatives_connexion', 0) + 1
                        db.q('UPDATE utilisateurs SET tentatives_connexion=? WHERE id=?', (nt, user['id']))
                        st.error(f"❌ Mot de passe incorrect. Reste : {max(0, 3-nt)} tentative(s).")
                else: st.error("❌ Email ou mot de passe incorrect")
            
            st.write("---")
            # RÉCUPÉRATION DE COMPTE
            with st.expander("❓ Mot de passe oublié / Récupération de compte"):
                if st.session_state.reset_step == 0:
                    st.info("Entrez votre email. Si le compte existe, un code de récupération s'affichera.")
                    reset_email = st.text_input("📧 Votre adresse email", key="reset_email_input")
                    if st.button("🔍 Vérifier l'email", key="btn_check_email"):
                        u = db.f1("SELECT id FROM utilisateurs WHERE email=%s", (reset_email.lower().strip(),))
                        if u:
                            code = str(random.randint(100000, 999999))
                            db.q("INSERT INTO reset_codes (email, code, expires_at) VALUES (%s, %s, NOW() + INTERVAL '15 minutes')", (reset_email.lower().strip(), code))
                            st.session_state.reset_email = reset_email.lower().strip()
                            st.session_state.reset_code_gen = code
                            st.session_state.reset_step = 1
                            st.rerun()
                        else:
                            st.error("❌ Aucun compte trouvé avec cet email.")
                elif st.session_state.reset_step == 1:
                    st.success(f"✅ Code généré avec succès !")
                    st.warning(f"👉 **Votre code de récupération est : `{st.session_state.reset_code_gen}`** (valable 15 min).\nNote : Dans une version future, ce code sera envoyé par email.")
                    code_input = st.text_input("🔢 Saisissez le code reçu")
                    new_pwd = st.text_input("🔑 Nouveau mot de passe", type="password")
                    confirm_pwd = st.text_input("🔑 Confirmer le mot de passe", type="password")
                    if st.button("🔄 Réinitialiser", key="btn_reset_pwd"):
                        if code_input != st.session_state.reset_code_gen:
                            st.error("❌ Code incorrect.")
                        elif len(new_pwd) < 6:
                            st.error("❌ Mot de passe trop court (min 6).")
                        elif new_pwd != confirm_pwd:
                            st.error("❌ Les mots de passe ne correspondent pas.")
                        else:
                            db.q("UPDATE utilisateurs SET password_hash=%s, tentatives_connexion=0, bloque=0 WHERE email=%s", (hash_pwd(new_pwd), st.session_state.reset_email))
                            db.q("UPDATE reset_codes SET used=1 WHERE email=%s AND code=%s", (st.session_state.reset_email, st.session_state.reset_code_gen))
                            st.success("✅ Mot de passe réinitialisé ! Connectez-vous.")
                            st.session_state.reset_step = 0
                            time.sleep(2)
                            st.rerun()

        with tab2:
            st.subheader("Créer un compte")
            with st.form(key=f"reg_form_{st.session_state.register_form_key}"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("👤 Nom")
                prenom = c2.text_input("👤 Prénom")
                email_r = st.text_input("📧 Email")
                password = st.text_input("🔑 Mot de passe (min 6)", type="password")
                pwd_confirm = st.text_input("🔑 Confirmer", type="password")
                st.info("💡 14 jours d'essai gratuit à l'inscription.")
                if st.form_submit_button("✨ S'inscrire", use_container_width=True, type="primary"):
                    if not all([nom, prenom, email_r, password]): st.error("Remplissez tous les champs")
                    elif len(password) < 6: st.error("Mot de passe trop court")
                    elif password != pwd_confirm: st.error("Les mots de passe ne correspondent pas")
                    else:
                        if db.q('INSERT INTO utilisateurs (nom,prenom,email,password_hash) VALUES (?,?,?,?)', (nom, prenom, email_r.lower(), hash_pwd(password))):
                            nu = db.f1('SELECT id FROM utilisateurs WHERE email=%s', (email_r.lower(),))
                            creer_essai(nu['id'])
                            st.success("✅ Compte créé ! Vous pouvez vous connecter.")
                            st.session_state.register_form_key += 1
                            st.rerun()
                        else: st.error("❌ Cet email est déjà utilisé")

# ========== APPRENANT ==========
elif st.session_state.logged_in and not st.session_state.is_admin:
    display_logo()
    uid = st.session_state.user['id']
    acces = a_acces_quiz(uid)
    jr = jours_restants(uid)

    st.markdown(f"""
    <div class="header-main">
        <h1>👋 Bienvenue {safe(st.session_state.user,'prenom','Apprenant')}!</h1>
        <p>{'Accès actif — ' + str(jr) + ' jours restants' if acces else 'Abonnement expiré'}</p>
    </div>
    """, unsafe_allow_html=True)

    uf = db.f1('SELECT * FROM utilisateurs WHERE id=?', (uid,))
    if uf and uf.get('last_activity'):
        try:
            last = uf['last_activity']
            dt = last.replace(tzinfo=None) if isinstance(last, datetime) else datetime.strptime(last.split('.')[0].replace('T',' '), '%Y-%m-%d %H:%M:%S') if isinstance(last, str) else datetime.now()
            rem = max(0, (uf.get('session_minutes', 120) or 120) - int((datetime.now() - dt).total_seconds()/60))
            cls = "timeout-green" if rem > 10 else "timeout-orange" if rem > 0 else "timeout-red"
            st.markdown(f"<div class='timeout-indicator {cls}'>⏱️ {rem} min</div>", unsafe_allow_html=True)
        except: pass

    nb = len(db.fa('SELECT id FROM resultats WHERE utilisateur_id=%s', (uid,)))
    moy = db.f1('SELECT AVG(pourcentage) AS m FROM resultats WHERE utilisateur_id=%s', (uid,))
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📝 Quiz complétés", nb)
    c2.metric("📊 Moyenne", f"{moy['m']:.0f}%" if moy and moy['m'] else "—")
    c3.metric("⏱️ Abonnement", f"{jr} jours" if acces else "Expiré")

    t1, t2, t3 = st.tabs(["📚 Quiz", "📊 Résultats", "📝 Feedback"])

    with t1:
        if not acces:
            afficher_paywall(uid, safe(st.session_state.user, 'prenom'))
        else:
            series = db.fa('SELECT * FROM series')
            if series:
                st.subheader("Choisissez une série")
                cols = st.columns(2)
                for idx, s in enumerate(series):
                    qs = db.fa('SELECT * FROM quiz WHERE series_id=?', (s['id'],))
                    with cols[idx % 2]:
                        if s.get('image_data'):
                            st.markdown(f"""
                            <div class="card-quiz" style="padding:0;">
                                <img src="{s['image_data']}" style="width:100%;height:180px;object-fit:cover;border-radius:18px 18px 0 0;">
                                <div style="padding:20px;">
                                    <div class="card-quiz-title">{safe(s,'nom')}</div>
                                    <div class="card-quiz-desc">{s['description']}</div>
                                    <div class="card-quiz-count">🎯 {len(qs)} questions</div>
                                </div>
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="card-quiz">
                                <div style="font-size:3em;">📚</div>
                                <div class="card-quiz-title">{safe(s,'nom')}</div>
                                <div class="card-quiz-desc">{s['description']}</div>
                                <div class="card-quiz-count">🎯 {len(qs)} questions</div>
                            </div>""", unsafe_allow_html=True)
                        if st.button(f"Commencer {s['nom']}", key=f"q_{s['id']}", use_container_width=True):
                            st.session_state.page = f"quiz_{s['id']}"
                            st.session_state.current_series_id = s['id']
                            st.session_state.current_quizzes = qs
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_submitted = False
                            st.rerun()

            for s in series:
                if st.session_state.page == f"quiz_{s['id']}" and st.session_state.current_quizzes:
                    qs = st.session_state.current_quizzes
                    if st.session_state.quiz_submitted:
                        display_correction(qs, st.session_state.quiz_answers, s)
                        c1, c2 = st.columns(2)
                        if c1.button("🔄 Recommencer", use_container_width=True):
                            st.session_state.quiz_answers = {}; st.session_state.quiz_submitted = False; st.rerun()
                        if c2.button("📚 Autre série", use_container_width=True):
                            st.session_state.page = "home"; st.session_state.quiz_answers = {}; st.session_state.quiz_submitted = False; st.session_state.current_quizzes = []; st.rerun()
                    else:
                        st.markdown(f"""
                        <div class="header-main" style="text-align:center;">
                            <h2>📖 {s['nom']}</h2>
                            <p>{s['description']}</p>
                        </div>""", unsafe_allow_html=True)
                        
                        prog = len([v for v in st.session_state.quiz_answers.values() if v]) / len(qs) if qs else 0
                        st.markdown(f"""
                        <div class="progress-container">
                            <div style="display:flex;justify-content:space-between;">
                                <span style="font-weight:700;color:#667eea;">Progression</span>
                                <span>{int(prog*100)}%</span>
                            </div>
                            <div class="progress-bar"><div class="progress-fill" style="width:{prog*100}%"></div></div>
                        </div>""", unsafe_allow_html=True)

                        for idx, q in enumerate(qs, 1):
                            st.markdown(f"""
                            <div class="question-box">
                                <div class="question-number">Question {idx}/{len(qs)}</div>
                                <div class="question-text">{q['question']}</div>
                            </div>""", unsafe_allow_html=True)
                            
                            opts = ["A", "B", "C", "D"]
                            txts = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
                            corr = [c.strip() for c in q['reponses_correctes'].split(",")]
                            
                            if len(corr) > 1:
                                st.markdown("<div style='color:#667eea;font-weight:700;margin:5px 0 10px 0;font-size:0.95em;'>🔘 Plusieurs réponses possibles</div>", unsafe_allow_html=True)
                                sel = []
                                for l, t in zip(opts, txts):
                                    if st.checkbox(f"{l}) {t}", key=f"q_{q['id']}_{l}"): sel.append(l)
                                st.session_state.quiz_answers[q['id']] = sel
                            else:
                                sel = st.radio("Réponse:", opts, format_func=lambda x, ot=txts: f"{x}) {ot[ord(x)-65]}", key=f"q_{q['id']}", label_visibility="collapsed", index=None)
                                st.session_state.quiz_answers[q['id']] = [sel] if sel else []
                            st.write("")

                        c1, c2 = st.columns(2)
                        if c1.button("⬅️ Retour", use_container_width=True):
                            st.session_state.page = "home"; st.session_state.quiz_answers = {}; st.session_state.quiz_submitted = False; st.session_state.current_quizzes = []; st.rerun()
                        if c2.button("✅ Soumettre", use_container_width=True, type="primary"):
                            nonrep = [i for i, q in enumerate(qs, 1) if not st.session_state.quiz_answers.get(q['id'])]
                            if nonrep:
                                st.error(f"❌ Questions sans réponse : {', '.join(map(str, nonrep))}"); st.stop()
                            
                            score = 0
                            for q in qs:
                                u_list = set(st.session_state.quiz_answers.get(q['id']) or [])
                                c_list = set(c.strip() for c in q['reponses_correctes'].split(","))
                                if u_list == c_list: score += 1 # NOTATION STRICTE ICI
                            
                            pct = (score / len(qs)) * 100
                            db.q('INSERT INTO resultats (utilisateur_id,series_id,score,total,pourcentage) VALUES (?,?,?,?,?)', (uid, s['id'], score, len(qs), pct))
                            st.session_state.quiz_submitted = True
                            st.rerun()

    with t2:
        st.subheader("📊 Mon historique")
        res = db.fa('SELECT * FROM resultats WHERE utilisateur_id=? ORDER BY date_test DESC', (uid,))
        if res:
            for r in res:
                s = db.f1('SELECT nom FROM series WHERE id=?', (r['series_id'],))
                em = "🎉" if r['pourcentage'] >= 80 else "👍" if r['pourcentage'] >= 60 else "💪"
                st.markdown(f"""
                <div class="card-quiz">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <h3>{em} {safe(s, 'nom', 'Série supprimée')}</h3>
                            <p style="color:#666;">Score : <strong>{r['score']}/{r['total']}</strong></p>
                            <small>📅 {r['date_test']}</small>
                        </div>
                        <div style="font-size:2em;font-weight:bold;color:#667eea;">{r['pourcentage']:.1f}%</div>
                    </div>
                </div>""", unsafe_allow_html=True)
        else: st.info("Aucun résultat.")

        st.divider()
        st.markdown("### 🏆 Top 10")
        top = db.fa("""SELECT u.prenom, u.nom, COUNT(r.id) as nb, ROUND(AVG(r.pourcentage)::numeric, 1) as moy
                       FROM utilisateurs u JOIN resultats r ON r.utilisateur_id = u.id
                       GROUP BY u.id, u.prenom, u.nom HAVING COUNT(r.id) >= 3 ORDER BY moy DESC LIMIT 10""")
        if top:
            for i, t in enumerate(top, 1):
                em = ['🥇','🥈','🥉'][i-1] if i <= 3 else f"{i}."
                st.markdown(f"{em} **{safe(t,'prenom')} {safe(t,'nom')}** — {t['moy']}% ({t['nb']} quiz)")
        else: st.caption("Pas assez de données.")

    with t3:
        st.subheader("📝 Votre avis")
        tit = st.text_input("Titre")
        msg = st.text_area("Message")
        typ = st.selectbox("Type", ["💡 Suggestion", "🐛 Bug", "👍 Compliment", "❓ Question", "📣 Autre"])
        if st.button("📤 Envoyer", use_container_width=True, type="primary"):
            if tit and msg:
                db.q('INSERT INTO feedback (email,titre,message,type) VALUES (?,?,?,?)', (st.session_state.user['email'], tit, msg, typ))
                st.success("✅ Merci !")
            else: st.error("Remplissez tous les champs")

    if st.button("🚪 Déconnexion", use_container_width=True):
        for k, v in defaults.items(): st.session_state[k] = v if not isinstance(v, (dict, list)) else type(v)()
        st.rerun()

# ========== ADMIN ==========
elif st.session_state.logged_in and st.session_state.is_admin:
    display_logo()
    st.markdown("""
    <div class="header-main">
        <h1>🔐 Administration</h1>
        <p>Gestion de la plateforme</p>
    </div>
    """, unsafe_allow_html=True)

    perms = get_perms()
    p_sup = perms['supprimer_quiz']
    p_add_a = perms['ajouter_admin']
    p_blk_u = perms['bloquer_users']
    p_sup_u = perms['supprimer_users']
    p_sup_a = perms['supprimer_admins']

    if not perms['principal']: st.warning("ℹ️ Admin secondaire.")

    tabs = st.tabs(["📊 Dashboard", "📚 Séries", "🎯 Quizzes", "📤 Importer", "👥 Apprenants", "👨‍💼 Admins", "💾 BD", "🔧 Maintenance", "📢 Panneau", "💬 Feedback", "💰 Paiements", "⚙️ Paramètres"])

    with tabs[0]:
        cols = st.columns(5)
        stats = [("👥","Apprenants", len(db.fa('SELECT id FROM utilisateurs'))), ("📚","Séries", len(db.fa('SELECT id FROM series'))), ("🎯","Quizzes", len(db.fa('SELECT id FROM quiz'))), ("💰","Paiements", len(db.fa("SELECT id FROM paiements WHERE statut='en_attente'"))), ("💬","Feedbacks", len(db.fa('SELECT id FROM feedback')))]
        for c, (e,l,n) in zip(cols, stats):
            with c: st.markdown(f'<div class="stat-box"><div class="stat-box-label">{e} {l}</div><div class="stat-box-number">{n}</div></div>', unsafe_allow_html=True)

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<h4>Tests Récents</h4>", unsafe_allow_html=True)
            for r in db.fa('SELECT * FROM resultats ORDER BY date_test DESC LIMIT 5'):
                u = db.f1('SELECT * FROM utilisateurs WHERE id=?', (r['utilisateur_id'],))
                s = db.f1('SELECT * FROM series WHERE id=?', (r['series_id'],))
                if u and s:
                    em = "🎉" if r['pourcentage'] >= 80 else "👍" if r['pourcentage'] >= 60 else "💪"
                    st.markdown(f'<div class="admin-card"><strong>{em} {safe(u,"prenom")} {safe(u,"nom")}</strong><br>{safe(s,"nom")}<br><span style="color:#667eea;font-weight:700;">{r["pourcentage"]:.1f}%</span></div>', unsafe_allow_html=True)
        with c2:
            st.markdown("<h4>Utilisateurs Actifs</h4>", unsafe_allow_html=True)
            for u in db.fa('SELECT * FROM utilisateurs ORDER BY last_activity DESC LIMIT 5'):
                if u: st.markdown(f'<div class="admin-card"><strong>{safe(u,"prenom")} {safe(u,"nom")}</strong><br><small>{safe(u,"email")}</small></div>', unsafe_allow_html=True)

    with tabs[1]:
        st.subheader("📚 Séries")
        with st.expander("➕ Créer"):
            nom = st.text_input("Nom", key="s_nom")
            desc = st.text_area("Description", key="s_desc")
            img_f = st.file_uploader("🖼️ Image", type=["png","jpg","jpeg"], key="s_img")
            if st.button("Créer", type="primary"):
                if nom:
                    d = process_series_image(img_f) if img_f else None
                    if db.q('INSERT INTO series (nom,description,image_data) VALUES (?,?,?)', (nom, desc, d)):
                        st.success("✅ Créée !"); st.rerun()
                    else: st.error("❌ Existe déjà")
                else: st.error("Entrez un nom")
        st.write("---")
        for s in db.fa('SELECT * FROM series'):
            qc = len(db.fa('SELECT id FROM quiz WHERE series_id=?', (s['id'],)))
            c1, c2 = st.columns([3, 1])
            with c1:
                img = f'<img src="{s["image_data"]}" style="width:100%;height:150px;object-fit:cover;border-radius:10px;margin-bottom:10px;">' if s.get('image_data') else ""
                st.markdown(f'<div class="card-quiz">{img}<h3>{s["nom"]}</h3><p>{s["description"]}</p><small>🎯 {qc} quizzes</small></div>', unsafe_allow_html=True)
            with c2:
                with st.expander("🖼️ Image"):
                    ni = st.file_uploader("Changer", type=["png","jpg","jpeg"], key=f"se_img_{s['id']}", label_visibility="collapsed")
                    if ni:
                        nd = process_series_image(ni)
                        if nd: db.q('UPDATE series SET image_data=? WHERE id=?', (nd, s['id'])); st.rerun()
                if p_sup:
                    if st.button("🗑️", key=f"s_del_{s['id']}"):
                        db.q('DELETE FROM quiz WHERE series_id=?', (s['id'],)); db.q('DELETE FROM series WHERE id=?', (s['id'],)); st.rerun()

    with tabs[2]:
        st.subheader("🎯 Quizzes")
        series = db.fa('SELECT * FROM series')
        if not series: st.warning("Créez une série d'abord")
        else:
            st1, st2 = st.tabs(["Voir", "Créer"])
            with st1:
                sel = st.selectbox("Série", [(s['id'], s['nom']) for s in series], format_func=lambda x: x[1])
                for i, q in enumerate(db.fa('SELECT * FROM quiz WHERE series_id=?', (sel[0],)), 1):
                    c1, c2, c3 = st.columns([3, 0.5, 0.5])
                    with c1:
                        st.markdown(f'<div class="admin-card"><b>Q{i}: {q["question"]}</b><br><small>A) {q["option_a"]} | B) {q["option_b"]} | C) {q["option_c"]} | D) {q["option_d"]}</small><br><span style="color:#667eea;font-weight:bold;">✅ {q["reponses_correctes"]}</span></div>', unsafe_allow_html=True)
                    with c2:
                        if st.button("✏️", key=f"e_{q['id']}"): st.session_state.editing_quiz_id = q['id']; st.rerun()
                    with c3:
                        if p_sup:
                            if st.button("🗑️", key=f"d_{q['id']}"): db.q('DELETE FROM quiz WHERE id=?', (q['id'],)); st.rerun()
                    
                    if st.session_state.editing_quiz_id == q['id']:
                        with st.form(f"ef_{q['id']}"):
                            nq = st.text_area("Question", value=q['question'])
                            ca, cb, cc, cd = st.columns(4)
                            na = ca.text_input("A", value=q['option_a']); nb = cb.text_input("B", value=q['option_b'])
                            nc = cc.text_input("C", value=q['option_c']); nd = cd.text_input("D", value=q['option_d'])
                            ncor = st.multiselect("Correctes", ["A","B","C","D"], default=q['reponses_correctes'].split(","))
                            nex = st.text_area("Explication", value=q['explication'])
                            if st.form_submit_button("💾 Sauver", type="primary"):
                                db.q('UPDATE quiz SET question=?,option_a=?,option_b=?,option_c=?,option_d=?,reponses_correctes=?,explication=? WHERE id=?', (nq,na,nb,nc,nd,",".join(ncor),nex,q['id']))
                                st.session_state.editing_quiz_id = None; st.rerun()
                            if st.form_submit_button("❌ Annuler"): st.session_state.editing_quiz_id = None; st.rerun()

            with st2:
                selc = st.selectbox("Série", [(s['id'], s['nom']) for s in series], format_func=lambda x: x[1], key="c_sel")
                with st.form(f"cq_{st.session_state.quiz_form_key}"):
                    q = st.text_area("Question")
                    c1, c2, c3, c4 = st.columns(4)
                    oa = c1.text_input("A"); ob = c2.text_input("B"); oc = c3.text_input("C"); od = c4.text_input("D")
                    st.info("Cochez 1 ou plusieurs réponses correctes. La notation sera stricte.")
                    cor = st.multiselect("✅ Bonne(s) réponse(s)", ["A","B","C","D"])
                    ex = st.text_area("💡 Explication")
                    if st.form_submit_button("✅ Créer", type="primary"):
                        if q and oa and ob and oc and od and cor:
                            db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)', (selc[0],q,oa,ob,oc,od,",".join(cor),ex))
                            st.success("Créé !"); st.session_state.quiz_form_key += 1; st.rerun()
                        else: st.error("Remplissez tout")

    with tabs[3]:
        st.subheader("📤 Importer CSV")
        f = st.file_uploader("Fichier CSV (séparateur ;)", type=["csv"])
        if f:
            try:
                df = pd.read_csv(f, sep=";")
                ed = st.data_editor(df, use_container_width=True)
                sl = db.fa('SELECT * FROM series')
                if sl:
                    ss = st.selectbox("Série", [(s['id'], s['nom']) for s in sl], format_func=lambda x: x[1])
                    if st.button("📥 Importer"):
                        c = 0
                        for _, r in ed.iterrows():
                            db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)', (ss[0],r['question'],r['a'],r['b'],r['c'],r['d'],r['reponses_correctes'],r['explication']))
                            c += 1
                        st.success(f"{c} importés !"); st.rerun()
            except Exception as e: st.error(str(e))

    with tabs[4]:
        st.subheader("👥 Apprenants")
        for u in db.fa('SELECT * FROM utilisateurs'):
            if not u: continue
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1: st.markdown(f'**{safe(u,"prenom")} {safe(u,"nom")}**<br><small>{safe(u,"email")}</small>', unsafe_allow_html=True)
            with c2:
                if p_blk_u:
                    if st.button("🔒" if safe(u,'status')=='actif' else "✅", key=f"b_{u['id']}"):
                        db.q('UPDATE utilisateurs SET status=? WHERE id=?', ('bloqué' if safe(u,'status')=='actif' else 'actif', u['id'])); st.rerun()
            with c3:
                if p_blk_u:
                    v = int(safe(u,'session_minutes',120))
                    nd = st.number_input("Min", 5, 1440, v, key=f"m_{u['id']}")
                    if nd != v: db.q('UPDATE utilisateurs SET session_minutes=? WHERE id=?', (nd, u['id'])); st.rerun()
            with c4:
                if p_sup_u:
                    if st.button("🗑️", key=f"du_{u['id']}"): db.q('DELETE FROM utilisateurs WHERE id=?', (u['id'],)); st.rerun()
            st.divider()

    with tabs[5]:
        st.subheader("👨‍💼 Admins")
        if p_add_a:
            with st.form(f"ca_{st.session_state.admin_form_key}"):
                c1, c2 = st.columns(2)
                na = c1.text_input("Nom"); pa = c2.text_input("Prénom")
                ea = st.text_input("Email"); pwa = st.text_input("Mot de passe", type="password")
                c1, c2, c3 = st.columns(3)
                pd = c1.checkbox("Supprimer quiz"); ab = c2.checkbox("Ajouter admin")
                bl = c3.checkbox("Bloquer users"); su = c1.checkbox("Suppr users")
                sa = c2.checkbox("Suppr admins"); pay = c3.checkbox("Paiements")
                if st.form_submit_button("Créer", type="primary"):
                    if len(pwa)<8: st.error("Min 8 car.")
                    elif db.q('INSERT INTO admins (email,password_hash,nom,prenom,niveau_permission,peut_supprimer_quiz,peut_ajouter_admin,peut_bloquer_users,peut_supprimer_users,peut_supprimer_admins,peut_gerer_paiements) VALUES (?,?,?,?,?,?,?,?,?,?,?)', (ea.lower(),hash_pwd(pwa),na,pa,'secondaire',int(pd),int(ab),int(bl),int(su),int(sa),int(pay))):
                        st.success("Créé !"); st.session_state.admin_form_key += 1; st.rerun()
                    else: st.error("Email existe")
        
        for a in db.fa('SELECT * FROM admins'):
            if a['email'] == st.session_state.user.get('email'): continue
            c1, c2 = st.columns([3, 1])
            c1.markdown(f'**{safe(a,"prenom")} {safe(a,"nom")}** ({safe(a,"email")})')
            if p_sup_a and c2.button("🗑️", key=f"da_{a['id']}"): db.q('DELETE FROM admins WHERE id=?', (a['id'],)); st.rerun()
            st.divider()

    with tabs[6]:
        if perms['principal']:
            if st.button("📥 Exporter BD (JSON)", type="primary"):
                st.download_button("💾 Télécharger", data=json.dumps({"users":db.fa('SELECT * FROM utilisateurs')}, indent=2, default=str), file_name="backup.json")
            f = st.file_uploader("Importer JSON", type=["json"])
            if f and st.button("🔄 Restaurer"):
                try: st.success("OK (fonction simplifiée)"); st.rerun()
                except: st.error("Erreur")
        else: st.warning("🔒 Principal seulement")

    with tabs[7]:
        st.subheader("🔧 Maintenance")
        blocked = db.fa('SELECT * FROM utilisateurs WHERE bloque=1')
        if blocked:
            for b in blocked:
                c1, c2 = st.columns([3,1])
                c1.warning(f"🚫 {safe(b,'prenom')} {safe(b,'nom')} — {b.get('raison_blocage','')}")
                if p_blk_u and c2.button("Débloquer", key=f"ub_{b['id']}"):
                    db.q('UPDATE utilisateurs SET bloque=0, tentatives_connexion=0 WHERE id=?', (b['id'],)); st.rerun()
        else: st.success("Aucun compte bloqué")

    with tabs[8]:
        if perms['principal']:
            m = db.f1("SELECT * FROM maintenance ORDER BY id DESC LIMIT 1")
            act = (m.get('actif',0)==1) if m else False
            msg = m.get('message','') if m else ''
            st.info(f"Etat : {'🔧 MAINTENANCE' if act else '✅ EN LIGNE'}")
            with st.form("maint"):
                nm = st.text_area("Message", value=msg)
                c1, c2 = st.columns(2)
                t = c1.form_submit_button("Désactiver" if act else "Activer", type="primary")
                s = c2.form_submit_button("Sauver msg")
                if t:
                    ne = 0 if act else 1
                    if m: db.q("UPDATE maintenance SET actif=?, message=?, updated_at=NOW() WHERE id=?", (ne, nm, m['id']))
                    else: db.q("INSERT INTO maintenance (actif,message) VALUES (?,?)", (ne, nm))
                    st.rerun()
                if s:
                    if m: db.q("UPDATE maintenance SET message=? WHERE id=?", (nm, m['id']))
                    else: db.q("INSERT INTO maintenance (actif,message) VALUES (0,?)", (nm,))
                    st.rerun()
        else: st.warning("🔒 Principal seulement")

    with tabs[9]:
        st.subheader("💬 Feedbacks")
        for f in db.fa('SELECT * FROM feedback ORDER BY date_feedback DESC'):
            c1, c2 = st.columns([3,1])
            c1.markdown(f'<div class="admin-card"><b>{f["titre"]}</b> ({f["type"]})<br><small>{safe(f,"email")}</small><p>{f["message"]}</p></div>', unsafe_allow_html=True)
            if p_sup and c2.button("🗑️", key=f"df_{f['id']}"): db.q('DELETE FROM feedback WHERE id=?', (f['id'],)); st.rerun()

    with tabs[10]:
        if perms['gerer_paiements']:
            ps = db.fa("SELECT p.*, u.nom, u.prenom, u.email, o.nom as off, o.duree_jours FROM paiements p LEFT JOIN utilisateurs u ON u.id=p.utilisateur_id LEFT JOIN offres o ON o.id=p.offre_id WHERE p.statut='en_attente'")
            if not ps: st.success("Aucun en attente")
            for p in ps:
                with st.expander(f"💳 {safe(p,'prenom')} {safe(p,'nom')} — {p['montant']} FCFA"):
                    st.write(f"Réf : `{p['reference']}` | Offre : {safe(p,'off','?')} ({safe(p,'duree_jours','?')}j)")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Valider", key=f"vp_{p['id']}"):
                        prolonger_abo(p['utilisateur_id'], p['duree_jours'])
                        db.q("UPDATE paiements SET statut='valide', date_validation=NOW() WHERE id=%s", (p['id'],))
                        st.rerun()
                    if c2.button("❌ Rejeter", key=f"rp_{p['id']}"):
                        db.q("UPDATE paiements SET statut='rejete' WHERE id=%s", (p['id'],)); st.rerun()
        else: st.warning("🔒 Non autorisé")

    with tabs[11]:
        if perms['principal']:
            om = db.f1("SELECT valeur FROM parametres WHERE cle='orange_money_numero'")
            wa = db.f1("SELECT valeur FROM parametres WHERE cle='whatsapp_numero'")
            c1, c2 = st.columns(2)
            no = c1.text_input("Orange Money", value=om['valeur'] if om else '')
            nw = c2.text_input("WhatsApp", value=wa['valeur'] if wa else '')
            if st.button("💾 Sauver"):
                db.q("UPDATE parametres SET valeur=%s WHERE cle='orange_money_numero'", (no,))
                db.q("UPDATE parametres SET valeur=%s WHERE cle='whatsapp_numero'", (nw,))
                st.success("Sauvegardé !"); st.rerun()
            
            st.divider()
            st.markdown("### Offres")
            for o in db.fa('SELECT * FROM offres'):
                c1,c2,c3 = st.columns([2,1,1])
                c1.write(o['nom']); c2.write(f"{o['montant']} FCFA"); c3.write(f"{o['duree_jours']}j")
            with st.form("add_off"):
                n = st.text_input("Nom offre"); m = st.number_input("Montant", 0, 100000, 2000, 500); d = st.number_input("Jours", 1, 365, 30)
                if st.form_submit_button("Ajouter"):
                    db.q('INSERT INTO offres (nom,montant,duree_jours) VALUES (?,?,?)', (n,m,d)); st.rerun()
        else: st.warning("🔒 Principal seulement")

    if st.button("🚪 Déconnexion", use_container_width=True):
        for k, v in defaults.items(): st.session_state[k] = v if not isinstance(v, (dict, list)) else type(v)()
        st.rerun()
