"""
🎓 CAMPUS RÉUSSITE v12 — IMAGES + CHOIX MULTIPLE + FOND
✅ Hash PBKDF2 + migration auto SHA-256
✅ Permissions admin réelles
✅ Essai gratuit 14 jours paramétrable
✅ Paywall Orange Money manuel (validation admin)
✅ Offres paramétrables
✅ Dashboard apprenant + Top 10
✅ Fond d'image plein écran de la plateforme
✅ Choix multiple (checkbox) pour les quiz multi-réponses
✅ Images par série (upload admin)
"""

import streamlit as st
import pandas as pd
import json
import hashlib
import hmac
import time
import os
import base64
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Campus Réussite v12",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== CSS ==========
st.markdown("""
<style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .logo-container { display:flex; justify-content:center; margin:20px 0;
                       animation: fadeInDown 0.8s ease-out; }
    .logo-container img { height:120px; border-radius:15px;
                          box-shadow: 0 10px 30px rgba(102,126,234,0.3);
                          transition: all 0.3s ease; }
    .logo-container img:hover { transform: scale(1.05); }
    @keyframes fadeInDown { from { opacity:0; transform: translateY(-30px); }
                            to { opacity:1; transform: translateY(0); } }
    .header-main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   color:white; padding:40px; border-radius:20px; margin-bottom:30px;
                   box-shadow: 0 15px 40px rgba(0,0,0,0.15); text-align:center;
                   animation: slideInUp 0.8s ease-out; }
    .header-main h1 { font-size:2.8em; font-weight:700; margin-bottom:10px;
                      text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .header-main p { font-size:1.15em; opacity:0.95; font-weight:300; }
    @keyframes slideInUp { from { opacity:0; transform: translateY(30px); }
                           to { opacity:1; transform: translateY(0); } }
    .card-quiz { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                 color:white; padding:35px; border-radius:18px; margin:20px 0;
                 cursor:pointer; transition: all 0.4s cubic-bezier(0.175,0.885,0.32,1.275);
                 box-shadow: 0 8px 25px rgba(102,126,234,0.2);
                 border: 2px solid transparent; overflow:hidden; }
    .card-quiz:hover { transform: translateY(-10px) scale(1.02);
                       box-shadow: 0 20px 50px rgba(102,126,234,0.4);
                       border: 2px solid rgba(255,255,255,0.3); }
    .card-quiz-title { font-size:1.6em; font-weight:700; margin:15px 0; color:white; }
    .card-quiz-desc { font-size:1em; color:rgba(255,255,255,0.9); margin-bottom:15px; }
    .card-quiz-count { font-size:1.4em; font-weight:700; padding-top:15px;
                       border-top: 2px solid rgba(255,255,255,0.2); }
    .question-box { background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
                    padding:30px; border-radius:15px; margin:25px 0;
                    border-left: 6px solid #667eea;
                    box-shadow: 0 4px 15px rgba(102,126,234,0.1); }
    .question-number { font-size:0.9em; color:#667eea; font-weight:700;
                       text-transform:uppercase; letter-spacing:1px; margin-bottom:10px; }
    .question-text { font-size:1.5em; color:#1a1a1a; font-weight:700; line-height:1.6; }
    .progress-container { margin:30px 0; padding:20px; background:white;
                          border-radius:12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    .progress-bar { width:100%; height:12px; background:#e0e0e0;
                    border-radius:10px; overflow:hidden; margin-top:10px; }
    .progress-fill { height:100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                     transition: width 0.4s ease; border-radius:10px; }
    .correction-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                         color:white; padding:40px; border-radius:15px; margin-bottom:30px;
                         text-align:center; }
    .correction-header h2 { font-size:2.2em; font-weight:700; margin-bottom:15px; }
    .score-display { background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
                     color:white; padding:40px; border-radius:15px; text-align:center;
                     margin:30px 0; box-shadow: 0 10px 30px rgba(52,211,153,0.3); }
    .score-display.orange { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    .score-display.red { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
    .score-big { font-size:4em; font-weight:700; margin:20px 0; }
    .score-percentage { font-size:2.5em; font-weight:700; margin:15px 0; opacity:0.95; }
    .score-message { font-size:1.3em; margin-top:15px; font-weight:500; }
    .result-summary { background:white; padding:30px; border-radius:15px; margin:30px 0;
                      box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
    .summary-title { font-size:1.5em; font-weight:700; color:#1a1a1a; margin-bottom:20px; }
    .summary-stats { display:grid; grid-template-columns: repeat(3,1fr); gap:20px; }
    .stat-item { text-align:center; padding:20px;
                 background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
                 border-radius:10px; }
    .stat-label { color:#667eea; font-weight:700; font-size:0.95em; margin-bottom:10px; }
    .stat-value { font-size:2em; font-weight:700; color:#1a1a1a; }
    .timeout-indicator { position:fixed; top:20px; right:20px; background:white;
                         padding:15px 20px; border-radius:12px;
                         box-shadow: 0 4px 15px rgba(0,0,0,0.1); font-weight:700;
                         z-index:1000; border:2px solid #667eea; }
    .timeout-green { color:#10b981; border-color:#10b981; }
    .timeout-orange { color:#f59e0b; border-color:#f59e0b; animation: blink 1s infinite; }
    .timeout-red { color:#ef4444; border-color:#ef4444; animation: blink 0.5s infinite; }
    @keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0.5; } }
    .admin-card { background:white; padding:25px; border-radius:15px; margin:20px 0;
                  box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 5px solid #667eea; }
    .admin-card h3 { color:#667eea; margin-bottom:15px; }
    .stat-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color:white; padding:30px; border-radius:15px; text-align:center;
                margin:15px; box-shadow: 0 4px 15px rgba(102,126,234,0.2); }
    .stat-box-number { font-size:2.5em; font-weight:700; margin:10px 0; }
    .stat-box-label { font-size:0.95em; opacity:0.9; }
    .card { background:white; padding:20px; border-radius:12px; margin:15px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); overflow:hidden; }
    .paywall-om { background: linear-gradient(135deg,#ff7900,#ff9500); color:white;
                  padding:30px; border-radius:15px; text-align:center; margin:15px 0;
                  box-shadow: 0 10px 30px rgba(255,121,0,0.3); }
    .paywall-om-num { font-size:2.2em; font-weight:900; letter-spacing:2px; margin:15px 0; }
</style>
""", unsafe_allow_html=True)

# ========== DB CLASS ==========
import psycopg2
import psycopg2.extras
from psycopg2 import pool as pg_pool

def _show_db_error_page(etape, message, url_partielle=""):
    st.markdown("""
    <div style="background:#fff3cd;border:2px solid #ffc107;border-radius:15px;padding:30px;margin:20px 0;">
        <h2 style="color:#856404;">⚠️ Problème de Connexion Base de Données</h2>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.error(f"**Etape échouée:** {etape}")
        st.code(message, language="text")
    with col2:
        st.info("**URL détectée (masquée):**")
        st.code(url_partielle if url_partielle else "Aucune URL trouvée", language="text")
    st.markdown("---")
    st.markdown("### Checklist de diagnostic")
    checks = {
        "DATABASE_URL dans les secrets Streamlit": "share.streamlit.io → votre app → Settings → Secrets",
        "Port 6543 (pas 5432)": "Supabase → Project Settings → Database → Connection string → Use connection pooling",
        "Mot de passe sans caractères spéciaux": "Supabase → Project Settings → Database → Reset password",
        "Projet Supabase actif (pas en pause)": "Aller sur supabase.com → vérifier que le projet n'est pas en pause",
    }
    for check, solution in checks.items():
        with st.expander(f"Vérifier: {check}"):
            st.write(f"**Solution:** {solution}")
    if st.button("Rafraichir pour retenter", type="primary", use_container_width=True):
        st.rerun()
    st.stop()


@st.cache_resource
def get_pool(url: str):
    try:
        p = pg_pool.ThreadedConnectionPool(
            minconn=1, maxconn=5, dsn=url, sslmode="require",
            connect_timeout=10, keepalives=1, keepalives_idle=30,
            keepalives_interval=10, keepalives_count=5,
        )
        return p
    except psycopg2.OperationalError as e:
        msg = str(e)
        conseil = ""
        if "Cannot assign requested address" in msg or ":5432" in msg:
            conseil = "\n\nCAUSE: Port 5432 bloqué. Utiliser port 6543 (pooler Supabase)."
        elif "password authentication" in msg:
            conseil = "\n\nCAUSE: Mot de passe incorrect dans DATABASE_URL."
        elif "missing key/value" in msg or "invalid dsn" in msg.lower():
            conseil = "\n\nCAUSE: Caractères spéciaux dans le mot de passe. Changer le mdp."
        _show_db_error_page("Création du pool de connexions", msg + conseil, url[:40] + "...")
    except Exception as e:
        _show_db_error_page("Erreur inattendue (pool)", str(e), url[:40] + "...")


class DB:
    def __init__(self):
        self._url  = self._get_url()
        self._pool = get_pool(self._url)
        self.init()

    def _get_url(self):
        if "DATABASE_URL" not in st.secrets:
            _show_db_error_page("Lecture DATABASE_URL",
                "Clé DATABASE_URL introuvable dans Settings → Secrets.", "AUCUNE URL")
        url = st.secrets["DATABASE_URL"]
        if not url or not url.startswith("postgresql"):
            _show_db_error_page("Format URL",
                f"L'URL doit commencer par 'postgresql'.\nActuel: {url[:40]}", url[:40])
        return self._encoder_url(url)

    def _encoder_url(self, url):
        from urllib.parse import quote, urlparse, urlunparse
        try:
            parsed = urlparse(url)
            if parsed.password:
                mdp = quote(parsed.password, safe="")
                netloc = parsed.netloc.replace(f":{parsed.password}@", f":{mdp}@")
                url = urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
        except Exception:
            pass
        return url

    def _masquer_url(self):
        try:
            parts = self._url.split("@")
            return f"{parts[0].split(':')[0]}:****@{parts[1]}"
        except Exception:
            return "URL_INVALIDE"

    def _conn(self):
        try:
            return self._pool.getconn()
        except Exception as e:
            _show_db_error_page("Connexion pool", str(e), self._masquer_url())

    def _release(self, conn):
        try:
            self._pool.putconn(conn)
        except Exception:
            pass

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
                    bloque INTEGER DEFAULT 0,
                    date_blocage TEXT, raison_blocage TEXT)""",
                """CREATE TABLE IF NOT EXISTS admins (
                    id SERIAL PRIMARY KEY, email TEXT UNIQUE,
                    password_hash TEXT, nom TEXT, prenom TEXT,
                    niveau_permission TEXT DEFAULT 'secondaire',
                    peut_supprimer_quiz INTEGER DEFAULT 0,
                    peut_ajouter_admin INTEGER DEFAULT 0,
                    peut_bloquer_users INTEGER DEFAULT 0,
                    peut_supprimer_users INTEGER DEFAULT 0,
                    peut_supprimer_admins INTEGER DEFAULT 0,
                    date_creation TIMESTAMP DEFAULT NOW(),
                    status TEXT DEFAULT 'actif')""",
                "ALTER TABLE admins ADD COLUMN IF NOT EXISTS peut_bloquer_users INTEGER DEFAULT 0",
                "ALTER TABLE admins ADD COLUMN IF NOT EXISTS peut_supprimer_users INTEGER DEFAULT 0",
                "ALTER TABLE admins ADD COLUMN IF NOT EXISTS peut_supprimer_admins INTEGER DEFAULT 0",
                "ALTER TABLE admins ADD COLUMN IF NOT EXISTS peut_gerer_paiements INTEGER DEFAULT 0",
                """CREATE TABLE IF NOT EXISTS series (
                    id SERIAL PRIMARY KEY, nom TEXT UNIQUE,
                    description TEXT, nombre_questions INTEGER DEFAULT 0)""",
                "ALTER TABLE series ADD COLUMN IF NOT EXISTS image_data TEXT",
                """CREATE TABLE IF NOT EXISTS maintenance (
                    id SERIAL PRIMARY KEY, actif INTEGER DEFAULT 0,
                    message TEXT DEFAULT '', updated_at TIMESTAMP DEFAULT NOW())""",
                """CREATE TABLE IF NOT EXISTS quiz (
                    id SERIAL PRIMARY KEY, series_id INTEGER,
                    question TEXT, option_a TEXT, option_b TEXT,
                    option_c TEXT, option_d TEXT,
                    reponses_correctes TEXT, explication TEXT)""",
                """CREATE TABLE IF NOT EXISTS resultats (
                    id SERIAL PRIMARY KEY, utilisateur_id INTEGER,
                    series_id INTEGER, score INTEGER, total INTEGER,
                    pourcentage REAL, date_test TIMESTAMP DEFAULT NOW())""",
                """CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY, email TEXT, titre TEXT,
                    message TEXT, type TEXT,
                    date_feedback TIMESTAMP DEFAULT NOW())""",
                """CREATE TABLE IF NOT EXISTS reponses_quiz (
                    id SERIAL PRIMARY KEY, resultat_id INTEGER,
                    quiz_id INTEGER, reponse_utilisateur TEXT,
                    reponses_correctes TEXT)""",
                """CREATE TABLE IF NOT EXISTS parametres (
                    cle TEXT PRIMARY KEY, valeur TEXT,
                    updated_at TIMESTAMP DEFAULT NOW())""",
                """CREATE TABLE IF NOT EXISTS offres (
                    id SERIAL PRIMARY KEY, nom TEXT,
                    montant INTEGER, duree_jours INTEGER,
                    actif INTEGER DEFAULT 1, ordre INTEGER DEFAULT 0)""",
                """CREATE TABLE IF NOT EXISTS abonnements (
                    id SERIAL PRIMARY KEY, utilisateur_id INTEGER,
                    date_debut TIMESTAMP DEFAULT NOW(),
                    date_fin TIMESTAMP, type TEXT DEFAULT 'essai',
                    statut TEXT DEFAULT 'actif', notes TEXT)""",
                """CREATE TABLE IF NOT EXISTS paiements (
                    id SERIAL PRIMARY KEY, utilisateur_id INTEGER,
                    offre_id INTEGER, montant INTEGER,
                    reference TEXT, notes TEXT,
                    statut TEXT DEFAULT 'en_attente',
                    date_soumission TIMESTAMP DEFAULT NOW(),
                    date_validation TIMESTAMP, valide_par TEXT)""",
            ]
            for sql in tables:
                c.execute(sql)

            c.execute("SELECT 1 FROM parametres WHERE cle='orange_money_numero'")
            if not c.fetchone():
                for k, v in [
                    ('orange_money_numero', 'À CONFIGURER'),
                    ('whatsapp_numero', '+226 XX XX XX XX'),
                    ('duree_essai_jours', '14'),
                ]:
                    c.execute("INSERT INTO parametres (cle,valeur) VALUES (%s,%s)", (k, v))

            c.execute("SELECT 1 FROM offres LIMIT 1")
            if not c.fetchone():
                for nom, montant, duree in [('1 mois', 2000, 30), ('3 mois', 5000, 90), ('6 mois', 9000, 180)]:
                    c.execute("INSERT INTO offres (nom,montant,duree_jours) VALUES (%s,%s,%s)",
                              (nom, montant, duree))

            c.execute("""INSERT INTO abonnements (utilisateur_id, date_fin, type)
                         SELECT u.id, NOW() + INTERVAL '14 days', 'essai'
                         FROM utilisateurs u
                         LEFT JOIN abonnements a ON a.utilisateur_id = u.id
                         WHERE a.id IS NULL""")

            conn.commit()
        except Exception as e:
            conn.rollback()
            _show_db_error_page("Création des tables", str(e), self._masquer_url())
        finally:
            self._release(conn)

    def q(self, sql, p=()):
        sql = sql.replace("?", "%s")
        conn = self._conn()
        try:
            c = conn.cursor()
            c.execute(sql, p)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            st.warning(f"Erreur BD (écriture): {str(e)[:150]}")
            return False
        finally:
            self._release(conn)

    def f1(self, sql, p=()):
        sql = sql.replace("?", "%s")
        conn = self._conn()
        try:
            c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            c.execute(sql, p)
            r = c.fetchone()
            return dict(r) if r else None
        except Exception as e:
            st.warning(f"Erreur BD (lecture): {str(e)[:150]}")
            return None
        finally:
            self._release(conn)

    def fa(self, sql, p=()):
        sql = sql.replace("?", "%s")
        conn = self._conn()
        try:
            c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            c.execute(sql, p)
            rows = c.fetchall()
            return [dict(r) for r in rows] if rows else []
        except Exception as e:
            st.warning(f"Erreur BD (liste): {str(e)[:150]}")
            return []
        finally:
            self._release(conn)


db = DB()


# ========== HASHING (PBKDF2) ==========
def hash_pwd(p):
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', p.encode(), salt, 200_000)
    return f"pbkdf2$200000${salt.hex()}${dk.hex()}"

def verify_pwd(p, h):
    if not h:
        return False
    if len(h) == 64 and all(c in '0123456789abcdef' for c in h):
        ancien = hashlib.sha256((p + "salt2024").encode()).hexdigest()
        return hmac.compare_digest(ancien, h)
    if h.startswith("pbkdf2$"):
        try:
            _, iter_s, salt_hex, hash_hex = h.split("$")
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(hash_hex)
            dk = hashlib.pbkdf2_hmac('sha256', p.encode(), salt, int(iter_s))
            return hmac.compare_digest(dk, expected)
        except Exception:
            return False
    return False

def _upgrade_hash(user_id, password, table='utilisateurs'):
    row = db.f1(f'SELECT password_hash FROM {table} WHERE id=%s', (user_id,))
    if row and row['password_hash']:
        h = row['password_hash']
        if not h.startswith("pbkdf2$"):
            db.q(f'UPDATE {table} SET password_hash=%s WHERE id=%s',
                 (hash_pwd(password), user_id))


# ========== HELPERS ==========
def safe(obj, key, defaut="N/A"):
    if obj is None:
        return defaut
    try:
        val = obj.get(key, defaut) if isinstance(obj, dict) else getattr(obj, key, defaut)
        return val if val is not None else defaut
    except Exception:
        return defaut


def get_perms():
    all_true = {k: True for k in ['principal','supprimer_quiz','ajouter_admin',
                                    'bloquer_users','supprimer_users','supprimer_admins',
                                    'gerer_paiements','gerer_parametres']}
    all_false = {k: False for k in all_true}
    if st.session_state.user.get('id', 0) == 0:
        return all_true
    adm = db.f1("SELECT * FROM admins WHERE email=%s", (st.session_state.user.get('email',''),))
    if not adm:
        return all_false
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


# ========== ABONNEMENT HELPERS ==========
def a_acces_quiz(user_id):
    r = db.f1('''SELECT id FROM abonnements
                 WHERE utilisateur_id=%s AND date_fin > NOW() LIMIT 1''', (user_id,))
    return r is not None

def jours_restants(user_id):
    r = db.f1('''SELECT EXTRACT(DAY FROM (date_fin - NOW()))::int AS jours
                 FROM abonnements
                 WHERE utilisateur_id=%s AND date_fin > NOW()
                 ORDER BY date_fin DESC LIMIT 1''', (user_id,))
    return r['jours'] if r and r['jours'] is not None else 0

def creer_essai(user_id):
    duree = db.f1("SELECT valeur FROM parametres WHERE cle='duree_essai_jours'")
    try:
        jours = int(duree['valeur']) if duree and duree['valeur'] else 14
    except Exception:
        jours = 14
    db.q('''INSERT INTO abonnements (utilisateur_id, date_fin, type)
            VALUES (%s, NOW() + INTERVAL '1 day' * %s, 'essai')''', (user_id, jours))

def prolonger_abo(user_id, jours):
    r = db.f1('''SELECT date_fin FROM abonnements
                 WHERE utilisateur_id=%s AND date_fin > NOW()
                 ORDER BY date_fin DESC LIMIT 1''', (user_id,))
    if r and r['date_fin']:
        db.q('''INSERT INTO abonnements (utilisateur_id, date_fin, type, statut)
                VALUES (%s, (SELECT date_fin FROM abonnements
                             WHERE utilisateur_id=%s AND date_fin > NOW()
                             ORDER BY date_fin DESC LIMIT 1) + INTERVAL '1 day' * %s,
                        'payant', 'actif')''', (user_id, user_id, jours))
    else:
        db.q('''INSERT INTO abonnements (utilisateur_id, date_fin, type, statut)
                VALUES (%s, NOW() + INTERVAL '1 day' * %s, 'payant', 'actif')''',
             (user_id, jours))


# ========== SESSION MANAGEMENT ==========
def check_session_timeout():
    if not st.session_state.logged_in or not st.session_state.user or st.session_state.is_admin:
        return
    try:
        user = db.f1('SELECT * FROM utilisateurs WHERE id=?', (st.session_state.user['id'],))
        if not user:
            return
        last_activity = user.get('last_activity')
        if not last_activity:
            db.q('UPDATE utilisateurs SET last_activity=NOW() WHERE id=?', (user['id'],))
            return
        if isinstance(last_activity, datetime):
            dt = last_activity.replace(tzinfo=None)
        elif isinstance(last_activity, str):
            last_activity = last_activity.split('.')[0].replace('T', ' ').strip()
            try:
                dt = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                dt = datetime.now()
        else:
            dt = datetime.now()
        timeout_minutes = user.get('session_minutes', 120) or 120
        elapsed = (datetime.now() - dt).total_seconds() / 60
        if elapsed > timeout_minutes:
            st.session_state.logged_in = False
            st.session_state.user = None
            st.warning("⏰ Session expirée! Reconnectez-vous.")
            st.rerun()
    except Exception:
        pass

def update_activity():
    if st.session_state.logged_in and st.session_state.user and not st.session_state.is_admin:
        now = time.time()
        last = st.session_state.get('_last_activity_push', 0)
        if now - last > 30:
            try:
                db.q('UPDATE utilisateurs SET last_activity=NOW() WHERE id=?',
                     (st.session_state.user['id'],))
                st.session_state._last_activity_push = now
            except Exception:
                pass


# ========== EXPORT/IMPORT ==========
def export_database():
    try:
        return json.dumps({
            'utilisateurs': db.fa('SELECT * FROM utilisateurs'),
            'admins': db.fa('SELECT * FROM admins'),
            'series': db.fa('SELECT * FROM series'),
            'quiz': db.fa('SELECT * FROM quiz'),
            'resultats': db.fa('SELECT * FROM resultats'),
            'feedback': db.fa('SELECT * FROM feedback'),
            'export_date': datetime.now().isoformat(),
            'version': '12.0'
        }, indent=2, default=str)
    except Exception:
        return None

def import_database(json_data):
    try:
        data = json.loads(json_data)
        db.init()
        for u in data.get('utilisateurs', []):
            db.q('INSERT INTO utilisateurs (nom,prenom,email,password_hash,role,status,session_minutes,last_activity) '
                 'VALUES (?,?,?,?,?,?,?,?) ON CONFLICT (email) DO NOTHING',
                 (u.get('nom'), u.get('prenom'), u.get('email'), u.get('password_hash'),
                  u.get('role'), u.get('status'), u.get('session_minutes', 120), u.get('last_activity')))
        for a in data.get('admins', []):
            db.q('INSERT INTO admins (email,password_hash,nom,prenom,date_creation,status) '
                 'VALUES (?,?,?,?,?,?) ON CONFLICT (email) DO NOTHING',
                 (a.get('email'), a.get('password_hash'), a.get('nom'),
                  a.get('prenom'), a.get('date_creation'), a.get('status', 'actif')))
        for s in data.get('series', []):
            db.q('INSERT INTO series (nom,description,nombre_questions) VALUES (?,?,?) ON CONFLICT (nom) DO NOTHING',
                 (s.get('nom'), s.get('description'), s.get('nombre_questions', 0)))
        for q in data.get('quiz', []):
            db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) '
                 'VALUES (?,?,?,?,?,?,?,?)',
                 (q.get('series_id'), q.get('question'), q.get('option_a'), q.get('option_b'),
                  q.get('option_c'), q.get('option_d'), q.get('reponses_correctes'), q.get('explication')))
        for r in data.get('resultats', []):
            db.q('INSERT INTO resultats (utilisateur_id,series_id,score,total,pourcentage,date_test) '
                 'VALUES (?,?,?,?,?,?)',
                 (r.get('utilisateur_id'), r.get('series_id'), r.get('score'),
                  r.get('total'), r.get('pourcentage'), r.get('date_test')))
        for f in data.get('feedback', []):
            db.q('INSERT INTO feedback (email,titre,message,type,date_feedback) VALUES (?,?,?,?,?)',
                 (f.get('email'), f.get('titre'), f.get('message'), f.get('type'), f.get('date_feedback')))
        return True
    except Exception:
        return False


# ========== INIT SESSION STATE ==========
defaults = {
    "logged_in": False, "is_admin": False, "user": None, "page": "home",
    "quiz_answers": {}, "quiz_submitted": False, "editing_quiz_id": None,
    "current_series_id": None, "current_quizzes": [], "correction_data": None,
    "register_form_key": 0, "quiz_form_key": 0, "serie_form_key": 0,
    "admin_form_key": 0, "_last_activity_push": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

check_session_timeout()
update_activity()


# ========== IMAGE / FOND HELPERS ==========
@st.cache_data
def _get_bg_b64():
    for fname in ["background.png", "background.jpg", "fond.png", "fond.jpg",
                  "campus.png", "campus.jpg", "logo.png"]:
        if os.path.exists(fname):
            try:
                with open(fname, "rb") as f:
                    data = base64.b64encode(f.read()).decode()
                ext = fname.split(".")[-1].lower()
                mime = "jpeg" if ext in ("jpg", "jpeg") else "png"
                return data, mime, fname
            except Exception:
                pass
    return None, None, None


def inject_background():
    data, mime, fname = _get_bg_b64()
    if not data:
        return
    st.markdown(f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {{
        background-image: 
            linear-gradient(135deg, rgba(245,247,250,0.88) 0%, rgba(195,207,226,0.88) 100%),
            url('data:image/{mime};base64,{data}');
        background-size: cover;
        background-position: center center;
        background-attachment: fixed;
        background-repeat: no-repeat;
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
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


# ========== AFFICHAGE HELPERS ==========
def display_logo():
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo.png", width=180, use_column_width=False)

def get_score_color(percentage):
    if percentage >= 80:
        return "green", "🎉 Excellent travail!", "#34d399"
    elif percentage >= 60:
        return "orange", "👍 Bon travail!", "#f59e0b"
    else:
        return "red", "💪 Continuez vos efforts!", "#ef4444"


def display_correction(quizzes, quiz_answers, serie):
    score = 0
    details = []
    for q in quizzes:
        user_raw = quiz_answers.get(q['id']) or []
        if isinstance(user_raw, str):
            user_list = [user_raw] if user_raw else []
        else:
            user_list = list(user_raw)
        correct_list = [c.strip() for c in q['reponses_correctes'].split(",")]
        is_correct = set(user_list) == set(correct_list)
        if is_correct:
            score += 1
        details.append({
            'question': q['question'],
            'user_list': user_list,
            'correct_answers': correct_list,
            'explication': q['explication'], 'is_correct': is_correct,
            'options_dict': {'A': q['option_a'], 'B': q['option_b'],
                             'C': q['option_c'], 'D': q['option_d']}
        })

    percentage = (score / len(quizzes)) * 100 if quizzes else 0
    color_type, message, color_code = get_score_color(percentage)

    st.markdown(f"""
    <div class="correction-header">
        <h2>📋 Votre Correction Détaillée</h2>
        <p>{serie['nom']}</p>
    </div>
    """, unsafe_allow_html=True)

    score_class = "score-display" if percentage >= 80 else "score-display orange" if percentage >= 60 else "score-display red"
    st.markdown(f"""
    <div class="{score_class}">
        <h2>✨ Quiz Complété!</h2>
        <div class="score-big">{score}/{len(quizzes)}</div>
        <div class="score-percentage">{percentage:.1f}%</div>
        <div class="score-message">{message}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="result-summary">
        <div class="summary-title">📊 Résumé de Votre Performance</div>
        <div class="summary-stats">
            <div class="stat-item"><div class="stat-label">✅ Bonnes réponses</div>
                <div class="stat-value" style="color:#10b981;">{score}</div></div>
            <div class="stat-item"><div class="stat-label">❌ Mauvaises réponses</div>
                <div class="stat-value" style="color:#ef4444;">{len(quizzes) - score}</div></div>
            <div class="stat-item"><div class="stat-label">📈 Pourcentage</div>
                <div class="stat-value" style="color:#667eea;">{percentage:.1f}%</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#1a1a1a;font-size:1.8em;margin:40px 0 30px 0;font-weight:700;'>🔍 Détail de Vos Réponses</h3>",
                unsafe_allow_html=True)

    for idx, detail in enumerate(details, 1):
        is_correct = detail['is_correct']
        status_badge = "✅ CORRECT" if is_correct else "❌ INCORRECT"
        badge_bg = "#d1fae5" if is_correct else "#fee2e2"
        badge_color = "#065f46" if is_correct else "#7f1d1d"
        border_color = "#10b981" if is_correct else "#ef4444"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#f0f4ff 0%,#f5f0ff 100%);
                    border-left:6px solid {border_color};padding:25px;border-radius:12px;
                    margin:20px 0 15px 0;box-shadow:0 4px 12px rgba(0,0,0,0.08);">
            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:15px;">
                <div style="font-weight:700;color:#667eea;font-size:1em;">Question {idx}/{len(details)}</div>
                <div style="background:{badge_bg};color:{badge_color};padding:6px 16px;
                            border-radius:20px;font-weight:700;font-size:0.9em;">{status_badge}</div>
            </div>
            <div style="font-size:1.3em;font-weight:700;color:#1a1a1a;line-height:1.6;">
                {detail['question']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if detail['user_list']:
                border = "#10b981" if is_correct else "#ef4444"
                bg = "#f0fdf4" if is_correct else "#fff5f5"
                lines = "".join([
                    f"<div style='background:white;padding:12px 15px;border-radius:6px;"
                    f"border-left:4px solid {border};font-weight:600;color:#1a1a1a;"
                    f"margin-top:8px;'>"
                    f"<span style='font-size:1.1em;font-weight:700;color:{border};'>{a}</span>) "
                    f"{detail['options_dict'].get(a, '')}</div>"
                    for a in sorted(detail['user_list'])
                ])
                st.markdown(f"""
                <div style="background:{bg};border-left:5px solid {border};padding:20px;
                            border-radius:8px;margin:15px 0;">
                    <div style="color:#667eea;font-weight:700;margin-bottom:10px;font-size:0.95em;">👤 Votre réponse</div>
                    {lines}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#fff5f5;border-left:5px solid #ef4444;padding:20px;
                            border-radius:8px;margin:15px 0;">
                    <div style="color:#667eea;font-weight:700;margin-bottom:10px;font-size:0.95em;">👤 Votre réponse</div>
                    <div style="background:white;padding:15px;border-radius:6px;color:#ef4444;font-weight:700;">
                        Non répondu
                    </div>
                </div>""", unsafe_allow_html=True)

        with col2:
            for correct_ans in detail['correct_answers']:
                txt = detail['options_dict'].get(correct_ans, 'Non trouvé')
                st.markdown(f"""
                <div style="background:#f0fdf4;border-left:5px solid #10b981;padding:20px;
                            border-radius:8px;margin:15px 0;">
                    <div style="color:#667eea;font-weight:700;margin-bottom:10px;font-size:0.95em;">✅ Bonne réponse</div>
                    <div style="background:white;padding:15px;border-radius:6px;
                                border-left:4px solid #10b981;font-weight:600;color:#1a1a1a;">
                        <span style="font-size:1.1em;font-weight:700;color:#10b981;">{correct_ans}</span>) {txt}
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%);padding:25px;
                    border-radius:10px;margin:20px 0 30px 0;border-left:5px solid #f59e0b;
                    box-shadow:0 4px 12px rgba(245,158,11,0.15);">
            <div style="font-weight:700;color:#92400e;margin-bottom:12px;font-size:1.05em;">💡 Explication</div>
            <div style="color:#78350f;line-height:1.7;font-size:1em;">{detail['explication']}</div>
        </div>""", unsafe_allow_html=True)

    return score, percentage


# ========== BANNIERE MAINTENANCE ==========
def afficher_banniere_maintenance():
    try:
        maint = db.f1("SELECT * FROM maintenance ORDER BY id DESC LIMIT 1")
        if maint and maint.get('actif', 0) == 1 and maint.get('message', '').strip():
            st.markdown(
                "<div style='background:linear-gradient(135deg,#f39c12,#e67e22);color:white;"
                "padding:18px 24px;border-radius:12px;margin-bottom:20px;text-align:center;"
                "font-size:1rem;font-weight:700;box-shadow:0 4px 15px rgba(243,156,18,0.4);'>"
                f"&#x1F527; <b>Maintenance en cours</b> &mdash; {maint['message']}"
                "</div>", unsafe_allow_html=True)
    except Exception:
        pass

afficher_banniere_maintenance()
inject_background()


# ========== PAYWALL ==========
def afficher_paywall(uid, prenom):
    st.markdown(f"""
    <div class="header-main" style="background:linear-gradient(135deg,#ef4444,#dc2626);">
        <h1>⏰ Votre essai gratuit est terminé</h1>
        <p>{prenom}, abonnez-vous pour continuer à accéder aux quiz</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("👋 Vous pouvez toujours **vous connecter**, consulter vos **résultats** et envoyer des **feedbacks**, mais les quiz sont verrouillés jusqu'à votre abonnement.")

    om = db.f1("SELECT valeur FROM parametres WHERE cle='orange_money_numero'") or {'valeur':'À CONFIGURER'}
    wa = db.f1("SELECT valeur FROM parametres WHERE cle='whatsapp_numero'") or {'valeur':'N/A'}
    offres = db.fa("SELECT * FROM offres WHERE actif=1 ORDER BY montant")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("### 📱 Payer par Orange Money")
        st.markdown(f"""
        <div class="paywall-om">
            <div style="font-size:0.9em;opacity:0.9;">Envoyez le montant au</div>
            <div class="paywall-om-num">{om['valeur']}</div>
            <div style="font-size:0.9em;opacity:0.9;">Orange Money</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        **📋 Comment payer :**
        1. Faites le dépôt Orange Money sur le numéro ci-dessus
        2. Prenez une **capture d'écran** du message de confirmation
        3. Envoyez la capture sur **WhatsApp : {wa['valeur']}**
        4. Remplissez le formulaire avec votre **référence de transaction**
        5. L'admin validera votre accès (généralement sous 2-24h)
        """)

    with col_b:
        st.markdown("### 💎 Choisir votre offre")
        if not offres:
            st.error("Aucune offre disponible — contactez l'administrateur.")
            return

        offre_choisie = st.selectbox(
            "Votre offre",
            [(o['id'], f"{o['nom']} — {o['montant']} FCFA ({o['duree_jours']} jours)") for o in offres],
            format_func=lambda x: x[1],
            key="offre_paywall"
        )

        en_attente = db.f1("""SELECT * FROM paiements WHERE utilisateur_id=%s
                              AND statut='en_attente' LIMIT 1""", (uid,))
        if en_attente:
            st.warning(f"⏳ Un paiement de **{en_attente['montant']} FCFA** est en attente de validation. Vous recevrez l'accès dès que l'admin aura vérifié.")
        else:
            with st.form("form_paiement_user", border=False):
                reference = st.text_input("🔢 Référence de transaction Orange Money *",
                    placeholder="Ex: MP250102.1234.A56789")
                notes = st.text_area("📝 Notes (optionnel)",
                    placeholder="Heure du dépôt, nom sur le compte Orange...")
                submit_pay = st.form_submit_button("📤 Envoyer pour validation",
                    use_container_width=True, type="primary")
                if submit_pay:
                    if not reference.strip():
                        st.error("❌ La référence de transaction est obligatoire")
                    else:
                        offre_info = next(o for o in offres if o['id'] == offre_choisie[0])
                        db.q('''INSERT INTO paiements
                            (utilisateur_id, offre_id, montant, reference, notes)
                            VALUES (?,?,?,?,?)''',
                            (uid, offre_info['id'], offre_info['montant'],
                             reference.strip(), notes))
                        st.success("✅ Paiement soumis ! L'admin va vérifier votre dépôt et valider votre accès.")
                        st.balloons()
                        st.rerun()


# ========== LOGIN PAGE ==========
if not st.session_state.logged_in:
    inject_background()
    display_logo()
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
            email = st.text_input("📧 Adresse email", key="login_email")
            pwd = st.text_input("🔑 Mot de passe", type="password", key="login_pwd")

            if st.button("✨ Se Connecter", use_container_width=True, type="primary"):
                try:
                    admins_secrets = st.secrets.get("admins", {})
                    if email.lower() in admins_secrets and admins_secrets[email.lower()] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.session_state.user = {'nom':'Principal','prenom':'Admin',
                                                 'email':email.lower(),'id':0}
                        st.success("✅ Connexion Admin réussie!")
                        st.rerun()
                except Exception:
                    pass

                admin = db.f1("SELECT * FROM admins WHERE email=? AND status='actif'", (email.lower(),))
                if admin and verify_pwd(pwd, admin['password_hash']):
                    _upgrade_hash(admin['id'], pwd, 'admins')
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.user = {k: v for k, v in admin.items() if k != 'password_hash'}
                    st.success("✅ Connexion Admin réussie!")
                    st.rerun()

                user = db.f1('SELECT * FROM utilisateurs WHERE email=?', (email.lower(),))
                if user:
                    if user.get('bloque', 0) == 1:
                        st.error(f"🚫 Compte bloqué: {user.get('raison_blocage', 'Contactez l\'admin')}")
                    elif user.get('status') == 'bloqué':
                        st.error("❌ Votre compte a été suspendu par l'administrateur")
                    elif user.get('tentatives_connexion', 0) >= 3:
                        db.q('UPDATE utilisateurs SET bloque=1, date_blocage=?, raison_blocage=? WHERE id=?',
                            (datetime.now().isoformat(), "3 tentatives échouées", user['id']))
                        st.error("🚫 Compte bloqué après 3 tentatives. Contactez l'administrateur.")
                    elif verify_pwd(pwd, user['password_hash']):
                        _upgrade_hash(user['id'], pwd, 'utilisateurs')
                        db.q('UPDATE utilisateurs SET tentatives_connexion=0, last_activity=NOW() WHERE id=?',
                            (user['id'],))
                        st.session_state.logged_in = True
                        st.session_state.user = {k: v for k, v in user.items() if k != 'password_hash'}
                        st.session_state.is_admin = False
                        st.success("✅ Bienvenue!")
                        st.rerun()
                    else:
                        new_t = user.get('tentatives_connexion', 0) + 1
                        db.q('UPDATE utilisateurs SET tentatives_connexion=? WHERE id=?', (new_t, user['id']))
                        reste = max(0, 3 - new_t)
                        if reste > 0:
                            st.error(f"❌ Mot de passe incorrect. Il vous reste {reste} tentative(s).")
                        else:
                            db.q('UPDATE utilisateurs SET bloque=1, date_blocage=?, raison_blocage=? WHERE id=?',
                                (datetime.now().isoformat(), "3 tentatives échouées", user['id']))
                            st.error("🚫 Compte bloqué après 3 tentatives. Contactez l'administrateur.")
                else:
                    st.error("❌ Email ou mot de passe incorrect")

        with tab2:
            st.subheader("📝 Créer un nouveau compte")
            with st.form(key=f"register_form_{st.session_state.register_form_key}", border=False):
                col_nom, col_prenom = st.columns(2)
                with col_nom:
                    nom = st.text_input("👤 Nom", placeholder="Votre nom de famille")
                with col_prenom:
                    prenom = st.text_input("👤 Prénom", placeholder="Votre prénom")
                email_r = st.text_input("📧 Adresse email", placeholder="exemple@email.com")
                password = st.text_input("🔑 Mot de passe (min 6 caractères)", type="password")
                pwd_confirm = st.text_input("🔑 Confirmer le mot de passe", type="password")
                st.info("💡 Vous bénéficiez de 14 jours d'essai gratuit à l'inscription.")
                submitted = st.form_submit_button("✨ S'inscrire", use_container_width=True, type="primary")

                if submitted:
                    if not nom or not prenom or not email_r or not password:
                        st.error("❌ Remplissez tous les champs")
                    elif len(password) < 6:
                        st.error("❌ Mot de passe trop court (minimum 6 caractères)")
                    elif password != pwd_confirm:
                        st.error("❌ Les mots de passe ne correspondent pas")
                    else:
                        ok = db.q('INSERT INTO utilisateurs (nom,prenom,email,password_hash) VALUES (?,?,?,?)',
                            (nom, prenom, email_r.lower(), hash_pwd(password)))
                        if ok:
                            new_user = db.f1('SELECT id FROM utilisateurs WHERE email=%s', (email_r.lower(),))
                            if new_user:
                                creer_essai(new_user['id'])
                            st.success("✅ Compte créé ! Votre essai gratuit de 14 jours commence maintenant.")
                            st.session_state.register_form_key += 1
                            st.rerun()
                        else:
                            st.error("❌ Cet email est déjà utilisé")


# ========== APPRENANT INTERFACE ==========
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

    user_full = db.f1('SELECT * FROM utilisateurs WHERE id=?', (uid,))
    if user_full:
        try:
            last_activity = user_full.get('last_activity')
            if last_activity:
                if isinstance(last_activity, datetime):
                    dt = last_activity.replace(tzinfo=None)
                elif isinstance(last_activity, str):
                    last_activity = last_activity.split('.')[0].replace('T', ' ').strip()
                    dt = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
                else:
                    dt = datetime.now()
                elapsed = int((datetime.now() - dt).total_seconds() / 60)
                timeout = user_full.get('session_minutes', 120) or 120
                remaining = max(0, timeout - elapsed)
                cls = "timeout-green" if remaining > 10 else "timeout-orange" if remaining > 0 else "timeout-red"
                st.markdown(f"""
                <div class="timeout-indicator {cls}">⏱️ {remaining}/{timeout} min restantes</div>
                """, unsafe_allow_html=True)
        except Exception:
            pass

    nb_quiz = len(db.fa('SELECT id FROM resultats WHERE utilisateur_id=%s', (uid,)))
    moyenne = db.f1('SELECT AVG(pourcentage) AS m FROM resultats WHERE utilisateur_id=%s', (uid,))
    moy_val = f"{moyenne['m']:.0f}%" if moyenne and moyenne['m'] is not None else "—"

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📝 Quiz complétés", nb_quiz)
    with c2: st.metric("📊 Moyenne", moy_val)
    with c3:
        if acces:
            st.metric("⏱️ Abonnement", f"{jr} jours restants")
        else:
            st.metric("⏱️ Abonnement", "Expiré")

    tab1, tab2, tab3 = st.tabs(["📚 Commencer un quiz", "📊 Mes résultats", "📝 Envoyer un feedback"])

    with tab1:
        if not acces:
            afficher_paywall(uid, safe(st.session_state.user, 'prenom', 'Cher apprenant'))
        else:
            series = db.fa('SELECT * FROM series')
            if series:
                st.subheader("Choisissez une série pour commencer")
                st.write("---")
                cols = st.columns(2)
                for idx, s in enumerate(series):
                    quizzes = db.fa('SELECT * FROM quiz WHERE series_id=?', (s['id'],))
                    with cols[idx % 2]:
                        if s.get('image_data'):
                            st.markdown(f"""
                            <div class="card-quiz" style="padding:0;overflow:hidden;">
                                <img src="{s['image_data']}" style="width:100%;height:200px;object-fit:cover;">
                                <div style="padding:30px;">
                                    <div class="card-quiz-title">{safe(s,'nom')}</div>
                                    <div class="card-quiz-desc">{s['description']}</div>
                                    <div class="card-quiz-count">🎯 {len(quizzes)} questions</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="card-quiz">
                                <div style="font-size:3em;">📚</div>
                                <div class="card-quiz-title">{safe(s,'nom')}</div>
                                <div class="card-quiz-desc">{s['description']}</div>
                                <div class="card-quiz-count">🎯 {len(quizzes)} questions</div>
                            </div>
                            """, unsafe_allow_html=True)
                        if st.button(f"Commencer {s['nom']}", key=f"quiz_{s['id']}",
                                     use_container_width=True):
                            st.session_state.page = f"quiz_{s['id']}"
                            st.session_state.current_series_id = s['id']
                            st.session_state.current_quizzes = quizzes
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_submitted = False
                            st.rerun()
            else:
                st.info("ℹ️ Aucun quiz disponible pour le moment.")

            for s in series:
                if st.session_state.page == f"quiz_{s['id']}" and st.session_state.current_quizzes:
                    quizzes = st.session_state.current_quizzes

                    if st.session_state.quiz_submitted:
                        display_correction(quizzes, st.session_state.quiz_answers, s)
                        st.write(""); st.write("---"); st.write("")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔄 Recommencer ce quiz", use_container_width=True):
                                st.session_state.quiz_answers = {}
                                st.session_state.quiz_submitted = False
                                st.rerun()
                        with col2:
                            if st.button("📚 Choisir une autre série", use_container_width=True):
                                st.session_state.page = "home"
                                st.session_state.quiz_answers = {}
                                st.session_state.quiz_submitted = False
                                st.session_state.current_quizzes = []
                                st.rerun()
                    else:
                        st.markdown(f"""
                        <div class="header-main" style="text-align:center;">
                            <h2>📖 {s['nom']}</h2>
                            <p>{s['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        progress = len([v for v in st.session_state.quiz_answers.values() if v]) / len(quizzes) if quizzes else 0
                        st.markdown(f"""
                        <div class="progress-container">
                            <div style="display:flex;justify-content:space-between;">
                                <span style="font-weight:700;color:#667eea;">Progression: {int(progress*100)}%</span>
                                <span style="color:#999;">{len([v for v in st.session_state.quiz_answers.values() if v])}/{len(quizzes)} répondu(e)s</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width:{progress*100}%"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.write("")
                        for idx, q in enumerate(quizzes, 1):
                            st.markdown(f"""
                            <div class="question-box">
                                <div class="question-number">Question {idx}/{len(quizzes)}</div>
                                <div class="question-text">{q['question']}</div>
                            </div>
                            """, unsafe_allow_html=True)

                            options = ["A", "B", "C", "D"]
                            option_texts = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
                            correct_list = [c.strip() for c in q['reponses_correctes'].split(",")]
                            is_multi = len(correct_list) > 1

                            if is_multi:
                                st.markdown("<div style='color:#667eea;font-weight:700;margin:5px 0 10px 0;font-size:0.95em;'>🔘 Plusieurs réponses possibles</div>", unsafe_allow_html=True)
                                selected = []
                                for letter, text in zip(options, option_texts):
                                    if st.checkbox(f"{letter}) {text}", key=f"q_{q['id']}_{letter}"):
                                        selected.append(letter)
                                st.session_state.quiz_answers[q['id']] = selected
                            else:
                                selected = st.radio(
                                    "Sélectionnez votre réponse:", options,
                                    format_func=lambda x, ot=option_texts: f"{x}) {ot[ord(x)-65]}",
                                    key=f"q_{q['id']}", label_visibility="collapsed", index=None)
                                st.session_state.quiz_answers[q['id']] = [selected] if selected else []
                            st.write("")

                        st.write("---")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button("⬅️ Retour", use_container_width=True):
                                st.session_state.page = "home"
                                st.session_state.quiz_answers = {}
                                st.session_state.quiz_submitted = False
                                st.session_state.current_quizzes = []
                                st.rerun()
                        with col2:
                            if st.button("✅ Soumettre les réponses", use_container_width=True, type="primary"):
                                unanswered = [i for i, q in enumerate(quizzes, 1)
                                              if not st.session_state.quiz_answers.get(q['id'])]
                                if unanswered:
                                    st.error(f"❌ Vous n'avez pas répondu aux questions: {', '.join(map(str, unanswered))}")
                                    st.stop()
                                score = 0
                                for q in quizzes:
                                    user_raw = st.session_state.quiz_answers.get(q['id']) or []
                                    user_set = set(user_raw) if isinstance(user_raw, list) else ({user_raw} if user_raw else set())
                                    correct_set = set(c.strip() for c in q['reponses_correctes'].split(","))
                                    if user_set == correct_set:
                                        score += 1
                                percentage = (score / len(quizzes)) * 100
                                db.q('INSERT INTO resultats (utilisateur_id,series_id,score,total,pourcentage) VALUES (?,?,?,?,?)',
                                    (uid, s['id'], score, len(quizzes), percentage))
                                st.session_state.quiz_submitted = True
                                st.session_state.current_series_id = s['id']
                                st.rerun()

    with tab2:
        st.subheader("📊 Votre historique de résultats")
        resultats = db.fa('SELECT * FROM resultats WHERE utilisateur_id=? ORDER BY date_test DESC', (uid,))
        if resultats:
            for res in resultats:
                serie = db.f1('SELECT * FROM series WHERE id=?', (res['series_id'],))
                nom_serie = safe(serie, 'nom', 'Série supprimée')
                emoji = "🎉" if res['pourcentage'] >= 80 else "👍" if res['pourcentage'] >= 60 else "💪"
                st.markdown(f"""
                <div class="card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <h3>{emoji} {nom_serie}</h3>
                            <p style="color:#666;">Résultat: <strong>{res['score']}/{res['total']}</strong></p>
                            <small>📅 {res['date_test']}</small>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:2em;font-weight:bold;color:#667eea;">{res['pourcentage']:.1f}%</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ Vous n'avez pas encore de résultats. Commencez un quiz!")

        st.divider()
        st.markdown("### 🏆 Top 10 des apprenants")
        top = db.fa("""SELECT u.prenom, u.nom,
                              COUNT(r.id) as nb,
                              ROUND(AVG(r.pourcentage)::numeric, 1) as moy
                       FROM utilisateurs u
                       JOIN resultats r ON r.utilisateur_id = u.id
                       GROUP BY u.id, u.prenom, u.nom
                       HAVING COUNT(r.id) >= 3
                       ORDER BY moy DESC LIMIT 10""")
        if top:
            for i, t in enumerate(top, 1):
                emoji = ['🥇','🥈','🥉'][i-1] if i <= 3 else f"{i}."
                st.markdown(f"{emoji} **{safe(t,'prenom')} {safe(t,'nom')}** — {t['moy']}% ({t['nb']} quiz)")
        else:
            st.caption("Pas encore assez de données pour un classement (3 quiz minimum par apprenant)")

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

    st.write("---")
    if st.button("🚪 Déconnexion", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v if not isinstance(v, (dict, list)) else type(v)()
        st.session_state.page = "home"
        st.rerun()


# ========== ADMIN INTERFACE ==========
elif st.session_state.logged_in and st.session_state.is_admin:
    display_logo()
    st.markdown("""
    <div class="header-main">
        <h1>🔐 Panneau d'Administration</h1>
        <p>Gestion complète de la plateforme</p>
    </div>
    """, unsafe_allow_html=True)

    perms = get_perms()
    est_admin_principal = perms['principal']
    peut_supprimer     = perms['supprimer_quiz']
    peut_ajouter_admin = perms['ajouter_admin']
    peut_bloquer_users = perms['bloquer_users']
    peut_suppr_users   = perms['supprimer_users']
    peut_suppr_admins  = perms['supprimer_admins']

    if not est_admin_principal:
        st.warning("ℹ️ Admin secondaire — certaines fonctionnalités sont restreintes.")

    admin_tabs = st.tabs([
        "📊 Dashboard", "📚 Séries", "🎯 Quizzes", "📤 Importer", "👥 Apprenants",
        "👨‍💼 Administrateurs", "💾 Base Données", "🔧 Maintenance",
        "📢 Panneau Maintenance", "💬 Feedback", "💰 Paiements", "⚙️ Paramètres"
    ])

    with admin_tabs[0]:
        st.markdown("<h2 style='color:#667eea;margin-bottom:30px;'>📊 Tableaux de Bord</h2>",
                    unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        stats = [
            ("👥", "Apprenants", len(db.fa('SELECT id FROM utilisateurs'))),
            ("📚", "Séries", len(db.fa('SELECT id FROM series'))),
            ("🎯", "Quizzes", len(db.fa('SELECT id FROM quiz'))),
            ("💰", "Paiements attente", len(db.fa("SELECT id FROM paiements WHERE statut='en_attente'"))),
            ("💬", "Feedbacks", len(db.fa('SELECT id FROM feedback'))),
        ]
        for col, (emoji, lbl, n) in zip([col1,col2,col3,col4,col5], stats):
            with col:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-box-label">{emoji} {lbl}</div>
                    <div class="stat-box-number">{n}</div>
                </div>""", unsafe_allow_html=True)

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h4>Tests Récents</h4>", unsafe_allow_html=True)
            for res in db.fa('SELECT * FROM resultats ORDER BY date_test DESC LIMIT 5'):
                u = db.f1('SELECT * FROM utilisateurs WHERE id=?', (res['utilisateur_id'],))
                s = db.f1('SELECT * FROM series WHERE id=?', (res['series_id'],))
                if not u or not s: continue
                emoji = "🎉" if res['pourcentage'] >= 80 else "👍" if res['pourcentage'] >= 60 else "💪"
                st.markdown(f"""
                <div class="admin-card">
                    <strong>{emoji} {safe(u,'prenom')} {safe(u,'nom')}</strong><br>
                    {safe(s,'nom')}<br>
                    <span style="color:#667eea;font-weight:700;">{res['pourcentage']:.1f}% ({res['score']}/{res['total']})</span>
                </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("<h4>Utilisateurs Actifs</h4>", unsafe_allow_html=True)
            for u in db.fa('SELECT * FROM utilisateurs ORDER BY last_activity DESC LIMIT 5'):
                if not u: continue
                st.markdown(f"""
                <div class="admin-card">
                    <strong>{safe(u,'prenom')} {safe(u,'nom')}</strong><br>
                    <span style="color:#666;font-size:0.9em;">{safe(u,'email')}</span><br>
                    <span style="color:#10b981;font-weight:700;">{'🟢 Actif' if safe(u,'status') == 'actif' else '🔴 Bloqué'}</span>
                </div>""", unsafe_allow_html=True)

    with admin_tabs[1]:
        st.subheader("📚 Gestion des Séries")
        with st.expander("➕ Créer une nouvelle série"):
            nom = st.text_input("Nom de la série", key="serie_nom")
            desc = st.text_area("Description", key="serie_desc")
            img_file = st.file_uploader("🖼️ Image de la série (optionnel — PNG/JPG, max 800x800)",
                                        type=["png", "jpg", "jpeg"], key="serie_img_new")
            if img_file:
                st.image(img_file, caption="Aperçu", width=250)
            if st.button("Créer la série", use_container_width=True, type="primary"):
                if nom:
                    img_data = process_series_image(img_file) if img_file else None
                    if db.q('INSERT INTO series (nom,description,image_data) VALUES (?,?,?)',
                            (nom, desc, img_data)):
                        st.success("✅ Série créée!")
                        st.rerun()
                    else:
                        st.error("❌ Cette série existe déjà")
                else:
                    st.error("❌ Entrez un nom")

        st.write("---")
        for s in db.fa('SELECT * FROM series'):
            quiz_count = len(db.fa('SELECT id FROM quiz WHERE series_id=?', (s['id'],)))
            col1, col2 = st.columns([3, 1])
            with col1:
                if s.get('image_data'):
                    st.markdown(f"""
                    <div class="card" style="padding:0;overflow:hidden;">
                        <img src="{s['image_data']}" style="width:100%;height:180px;object-fit:cover;">
                        <div style="padding:20px;">
                            <h3 style="color:#667eea;">{s['nom']}</h3>
                            <p style="color:#666;">{s['description']}</p>
                            <small style="color:#999;">🎯 {quiz_count} quizzes</small>
                        </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="card">
                        <h3>{s['nom']}</h3>
                        <p style="color:#666;">{s['description']}</p>
                        <small style="color:#999;">🎯 {quiz_count} quizzes</small>
                    </div>""", unsafe_allow_html=True)
            with col2:
                with st.expander("🖼️ Image"):
                    new_img = st.file_uploader("Changer", type=["png","jpg","jpeg"],
                                               key=f"serie_img_edit_{s['id']}",
                                               label_visibility="collapsed")
                    if new_img:
                        img_data = process_series_image(new_img)
                        if img_data:
                            db.q('UPDATE series SET image_data=? WHERE id=?', (img_data, s['id']))
                            st.success("✅ Image mise à jour")
                            st.rerun()
                if peut_supprimer:
                    if st.button("🗑️ Supprimer", key=f"serie_del_{s['id']}", use_container_width=True):
                        db.q('DELETE FROM quiz WHERE series_id=?', (s['id'],))
                        db.q('DELETE FROM series WHERE id=?', (s['id'],))
                        st.success("✅ Série supprimée")
                        st.rerun()
                else:
                    st.markdown("<small style='color:#999;'>🔒 Non autorisé</small>", unsafe_allow_html=True)

    with admin_tabs[2]:
        st.markdown("<h2 style='color:#667eea;'>🎯 Gestion des Quizzes</h2>", unsafe_allow_html=True)
        series = db.fa('SELECT * FROM series')
        if not series:
            st.warning("⚠️ Créez d'abord une série!")
        else:
            sub_tab1, sub_tab2 = st.tabs(["📋 Voir Quizzes", "➕ Créer Manuelle"])
            with sub_tab1:
                sel = st.selectbox("Sélectionner une série",
                    [(s['id'], s['nom']) for s in series], format_func=lambda x: x[1], key="view_series")
                st.divider()
                quizzes = db.fa('SELECT * FROM quiz WHERE series_id=?', (sel[0],))
                st.markdown(f"<h4>📚 {len(quizzes)} quizzes</h4>", unsafe_allow_html=True)
                for idx, q in enumerate(quizzes, 1):
                    col1, col2, col3 = st.columns([3, 0.5, 0.5])
                    with col1:
                        st.markdown(f"""
                        <div class="admin-card">
                            <strong>Q{idx}: {q['question']}</strong>
                            <div style="margin-top:15px;color:#666;">
                                <small>A) {q['option_a']}<br>B) {q['option_b']}<br>
                                C) {q['option_c']}<br>D) {q['option_d']}</small>
                            </div>
                            <div style="margin-top:10px;">
                                <span style="color:#667eea;font-weight:700;font-size:0.9em;">✅ Réponse(s): {q['reponses_correctes']}</span>
                            </div>
                            <div style="margin-top:10px;">
                                <small style="color:#999;">💡 {(q['explication'] or '')[:80]}...</small>
                            </div>
                        </div>""", unsafe_allow_html=True)
                    with col2:
                        if st.button("✏️", key=f"quiz_edit_{q['id']}", help="Éditer", use_container_width=True):
                            st.session_state.editing_quiz_id = q['id']
                            st.rerun()
                    with col3:
                        if peut_supprimer:
                            if st.button("🗑️", key=f"quiz_del_{q['id']}", help="Supprimer", use_container_width=True):
                                db.q('DELETE FROM quiz WHERE id=?', (q['id'],))
                                st.success("✅ Quiz supprimé!")
                                st.rerun()
                        else:
                            st.markdown("<small style='color:#999;'>🔒</small>", unsafe_allow_html=True)

                    if st.session_state.editing_quiz_id == q['id']:
                        st.divider()
                        st.markdown(f"### ✏️ Éditer Q{idx}")
                        with st.form(f"edit_form_{q['id']}", border=False):
                            new_q = st.text_area("Question", value=q['question'], height=80)
                            ca, cb, cc, cd = st.columns(4)
                            with ca: new_a = st.text_input("Option A", value=q['option_a'])
                            with cb: new_b = st.text_input("Option B", value=q['option_b'])
                            with cc: new_c = st.text_input("Option C", value=q['option_c'])
                            with cd: new_d = st.text_input("Option D", value=q['option_d'])
                            new_correct = st.multiselect("Réponses correctes",
                                ["A","B","C","D"], default=q['reponses_correctes'].split(","))
                            new_expl = st.text_area("Explication", value=q['explication'] or '', height=80)
                            cs, ccancel = st.columns(2)
                            with cs:
                                if st.form_submit_button("💾 Sauvegarder", use_container_width=True, type="primary"):
                                    db.q('UPDATE quiz SET question=?,option_a=?,option_b=?,option_c=?,option_d=?,reponses_correctes=?,explication=? WHERE id=?',
                                        (new_q, new_a, new_b, new_c, new_d, ",".join(new_correct), new_expl, q['id']))
                                    st.success("✅ Quiz modifié!")
                                    st.session_state.editing_quiz_id = None
                                    st.rerun()
                            with ccancel:
                                if st.form_submit_button("❌ Annuler", use_container_width=True):
                                    st.session_state.editing_quiz_id = None
                                    st.rerun()

            with sub_tab2:
                st.markdown("<h4 style='color:#667eea;'>➕ Créer un nouveau Quiz</h4>", unsafe_allow_html=True)
                sel_create = st.selectbox("Sélectionner la série",
                    [(s['id'], s['nom']) for s in series], format_func=lambda x: x[1], key="create_series")
                with st.form(f"create_quiz_form_{st.session_state.quiz_form_key}", border=False):
                    question = st.text_area("📝 Question", height=100)
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: option_a = st.text_input("Option A)")
                    with c2: option_b = st.text_input("Option B)")
                    with c3: option_c = st.text_input("Option C)")
                    with c4: option_d = st.text_input("Option D)")
                    st.divider()
                    reponses_correctes = st.multiselect("✅ Bonne(s) réponse(s) — sélectionnez-en plusieurs si applicable",
                        ["A","B","C","D"], default=[])
                    explication = st.text_area("💡 Explication", height=80)
                    st.divider()
                    submitted = st.form_submit_button("✅ Créer le Quiz", use_container_width=True, type="primary")
                    if submitted:
                        if question and option_a and option_b and option_c and option_d and reponses_correctes:
                            if db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)',
                                (sel_create[0], question, option_a, option_b, option_c, option_d,
                                 ",".join(reponses_correctes), explication)):
                                st.success("✅ Quiz créé!")
                                st.balloons()
                                st.session_state.quiz_form_key += 1
                                st.rerun()
                        else:
                            st.error("❌ Remplissez tous les champs obligatoires")

    with admin_tabs[3]:
        st.subheader("📤 Importer des Quizzes depuis CSV")
        uploaded_file = st.file_uploader("Sélectionnez un fichier CSV", type=["csv"])
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, sep=";")
                st.success(f"✅ {len(df)} quizzes chargés")
                edited_df = st.data_editor(df, use_container_width=True, height=400)
                series_list = db.fa('SELECT * FROM series')
                if series_list:
                    sel_series = st.selectbox("Ajouter à quelle série?",
                        [(s['id'], s['nom']) for s in series_list], format_func=lambda x: x[1])
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

    with admin_tabs[4]:
        st.subheader("👥 Gestion des Apprenants")
        users = db.fa('SELECT * FROM utilisateurs')
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-box-label">Total</div><div class="stat-box-number">{len(users)}</div></div>', unsafe_allow_html=True)
        with c2:
            active = len([u for u in users if u and safe(u,'status') == 'actif'])
            st.markdown(f'<div class="stat-box"><div class="stat-box-label">Actifs</div><div class="stat-box-number">{active}</div></div>', unsafe_allow_html=True)
        with c3:
            blocked = len([u for u in users if u and safe(u,'status') == 'bloqué'])
            st.markdown(f'<div class="stat-box"><div class="stat-box-label">Bloqués</div><div class="stat-box-number">{blocked}</div></div>', unsafe_allow_html=True)

        st.write("---")
        for u in users:
            if not u: continue
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                icon = "✅" if safe(u,'status') == 'actif' else "🔒"
                st.markdown(f"**{icon} {safe(u,'prenom')} {safe(u,'nom')}**")
                st.caption(f"📧 {safe(u,'email')}")
            with col2:
                if peut_bloquer_users:
                    if st.button("🔒 Bloquer" if safe(u,'status') == 'actif' else "✅ Débloquer",
                                 key=f"apprenant_block_{u['id']}", use_container_width=True):
                        new_status = 'bloqué' if safe(u,'status') == 'actif' else 'actif'
                        db.q('UPDATE utilisateurs SET status=? WHERE id=?', (new_status, u['id']))
                        st.rerun()
                else:
                    st.markdown("<small style='color:#999;'>🔒 Non autorisé</small>", unsafe_allow_html=True)
            with col3:
                if peut_bloquer_users:
                    val = safe(u, 'session_minutes', 120)
                    try:
                        val = int(val)
                    except Exception:
                        val = 120
                    new_dur = st.number_input("Min", 5, 1440, val,
                                             key=f"apprenant_dur_{u['id']}", step=1)
                    if new_dur != val:
                        db.q('UPDATE utilisateurs SET session_minutes=? WHERE id=?', (new_dur, u['id']))
                        st.rerun()
                else:
                    st.markdown("<small style='color:#999;'>🔒 Non autorisé</small>", unsafe_allow_html=True)
            with col4:
                if peut_suppr_users:
                    if st.button("🗑️ Supprimer", key=f"apprenant_del_{u['id']}", use_container_width=True):
                        db.q('DELETE FROM utilisateurs WHERE id=?', (u['id'],))
                        st.rerun()
                else:
                    st.markdown("<small style='color:#999;'>🔒 Non autorisé</small>", unsafe_allow_html=True)
            st.divider()

    with admin_tabs[5]:
        st.subheader("👨‍💼 Gestion des Administrateurs")
        if peut_ajouter_admin:
            with st.form(f"create_admin_form_{st.session_state.admin_form_key}", border=False):
                st.markdown("#### ➕ Créer un nouvel administrateur")
                ca, cb = st.columns(2)
                with ca:
                    nom_admin = st.text_input("Nom *")
                    email_admin = st.text_input("Email *")
                    pwd_admin = st.text_input("Mot de passe (min 8 car.) *", type="password")
                with cb:
                    prenom_admin = st.text_input("Prénom *")
                    pwd_admin_confirm = st.text_input("Confirmer *", type="password")
                st.markdown("---")
                pc1, pc2, pc3 = st.columns(3)
                with pc1:
                    p_quiz_del = st.checkbox("🗑️ Supprimer des quiz", value=False)
                with pc2:
                    p_user_blk = st.checkbox("🔒 Bloquer/Débloquer apprenants", value=False)
                    p_user_del = st.checkbox("🗑️ Supprimer apprenants", value=False)
                with pc3:
                    p_adm_add = st.checkbox("👨‍💼 Ajouter des admins", value=False)
                    p_adm_del = st.checkbox("🗑️ Supprimer des admins", value=False)
                    p_paiements = st.checkbox("💰 Gérer les paiements", value=False)

                submitted_admin = st.form_submit_button("✅ Créer l'administrateur",
                    use_container_width=True, type="primary")
                if submitted_admin:
                    if len(pwd_admin) < 8:
                        st.error("❌ Mot de passe trop court (8 caractères min.)")
                    elif pwd_admin != pwd_admin_confirm:
                        st.error("❌ Les mots de passe ne correspondent pas")
                    elif not all([nom_admin, prenom_admin, email_admin]):
                        st.error("❌ Remplissez tous les champs obligatoires")
                    else:
                        ok = db.q('''INSERT INTO admins (email,password_hash,nom,prenom,niveau_permission,
                                     peut_supprimer_quiz,peut_ajouter_admin,peut_bloquer_users,
                                     peut_supprimer_users,peut_supprimer_admins,peut_gerer_paiements)
                                     VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                            (email_admin.lower(), hash_pwd(pwd_admin), nom_admin, prenom_admin,
                             'secondaire',
                             1 if p_quiz_del else 0, 1 if p_adm_add else 0,
                             1 if p_user_blk else 0, 1 if p_user_del else 0,
                             1 if p_adm_del else 0, 1 if p_paiements else 0))
                        if ok:
                            st.success(f"✅ Admin créé: {email_admin}")
                            st.session_state.admin_form_key += 1
                            st.rerun()
                        else:
                            st.error("❌ Cet email est déjà utilisé")
        else:
            st.warning("🔒 Vous n'avez pas la permission d'ajouter des administrateurs.")

        st.write("---")
        for admin in db.fa('SELECT * FROM admins'):
            if not admin: continue
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                icon = "✅" if safe(admin,'status') == 'actif' else "🔒"
                st.markdown(f"**{icon} {safe(admin,'prenom')} {safe(admin,'nom')}**")
                st.caption(f"📧 {safe(admin,'email')}")
            with col2:
                if est_admin_principal and admin['email'] != st.session_state.user.get('email'):
                    if st.button("🔒" if safe(admin,'status') == 'actif' else "✅",
                                key=f"admin_block_{admin['id']}", use_container_width=True):
                        new_status = 'bloqué' if safe(admin,'status') == 'actif' else 'actif'
                        db.q('UPDATE admins SET status=? WHERE id=?', (new_status, admin['id']))
                        st.rerun()
                else:
                    st.markdown("<small style='color:#999;'>—</small>", unsafe_allow_html=True)
            with col3:
                if peut_suppr_admins and admin['email'] != st.session_state.user.get('email'):
                    if st.button("🗑️", key=f"admin_del_{admin['id']}", use_container_width=True):
                        db.q('DELETE FROM admins WHERE id=?', (admin['id'],))
                        st.rerun()
                else:
                    st.markdown("<small style='color:#999;'>—</small>", unsafe_allow_html=True)
            st.divider()

    with admin_tabs[6]:
        st.subheader("💾 Gestion de la Base de Données")
        if not est_admin_principal:
            st.warning("🔒 Réservé à l'administrateur principal.")
        else:
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
                            mime="application/json")
            with col2:
                st.markdown("### 📤 Importer")
                backup_file = st.file_uploader("Uploader une sauvegarde JSON", type=["json"])
                if backup_file:
                    try:
                        json_data = backup_file.read().decode("utf-8")
                        if st.button("🔄 Restaurer", use_container_width=True, type="primary"):
                            if import_database(json_data):
                                st.success("✅ Base de données restaurée!")
                                st.rerun()
                            else:
                                st.error("❌ Erreur de restauration")
                    except Exception:
                        st.error("❌ Fichier invalide")

            st.write("---")
            st.subheader("📊 Informations")
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1: st.metric("Utilisateurs", len(db.fa('SELECT id FROM utilisateurs')))
            with c2: st.metric("Admins", len(db.fa('SELECT id FROM admins')))
            with c3: st.metric("Séries", len(db.fa('SELECT id FROM series')))
            with c4: st.metric("Quizzes", len(db.fa('SELECT id FROM quiz')))
            with c5: st.metric("Résultats", len(db.fa('SELECT id FROM resultats')))
            with c6: st.metric("Paiements", len(db.fa('SELECT id FROM paiements')))

    with admin_tabs[7]:
        st.markdown("<h2 style='color:#667eea;'>🔧 Interface de Maintenance</h2>",
                    unsafe_allow_html=True)
        maint_t1, maint_t2, maint_t3 = st.tabs(["🚫 Comptes Bloqués", "📊 Statistiques", "⚙️ Outils"])

        with maint_t1:
            blocked = db.fa('SELECT * FROM utilisateurs WHERE bloque=1')
            if blocked:
                for bu in blocked:
                    cb1, cb2 = st.columns([3, 1])
                    with cb1:
                        st.markdown(f"""
                        <div class="admin-card" style="background:#ffe0e0;border-left-color:#ef4444;">
                            <strong>🚫 {safe(bu,'prenom')} {safe(bu,'nom')}</strong><br>
                            📧 {safe(bu,'email')}<br>
                            ❌ {bu.get('raison_blocage', 'N/A')}<br>
                            📅 {bu.get('date_blocage', 'N/A')}
                        </div>""", unsafe_allow_html=True)
                    with cb2:
                        if peut_bloquer_users:
                            if st.button("🔓 Débloquer", key=f"unblock_{bu['id']}", use_container_width=True):
                                db.q('UPDATE utilisateurs SET bloque=0, tentatives_connexion=0, raison_blocage=NULL WHERE id=?',
                                    (bu['id'],))
                                st.success(f"✅ {safe(bu,'prenom')} débloqué!")
                                st.rerun()
                        else:
                            st.markdown("<small>🔒</small>", unsafe_allow_html=True)
            else:
                st.success("✅ Aucun compte bloqué")

        with maint_t2:
            c1, c2, c3, c4, c5 = st.columns(5)
            stats_vals = [
                ("👥", "Utilisateurs", len(db.fa('SELECT id FROM utilisateurs'))),
                ("👨‍💼", "Admins", len(db.fa('SELECT id FROM admins'))),
                ("📚", "Séries", len(db.fa('SELECT id FROM series'))),
                ("🎯", "Quizzes", len(db.fa('SELECT id FROM quiz'))),
                ("🚫", "Bloqués", len(db.fa('SELECT id FROM utilisateurs WHERE bloque=1'))),
            ]
            for col, (e, l, v) in zip([c1,c2,c3,c4,c5], stats_vals):
                with col:
                    st.markdown(f'<div class="stat-box"><div class="stat-box-label">{e} {l}</div><div class="stat-box-number">{v}</div></div>',
                                unsafe_allow_html=True)

        with maint_t3:
            ct1, ct2 = st.columns(2)
            with ct1:
                if peut_bloquer_users:
                    if st.button("🔓 Débloquer TOUS les comptes", use_container_width=True):
                        db.q('UPDATE utilisateurs SET bloque=0, tentatives_connexion=0')
                        st.success("✅ Tous les comptes débloqués!")
                        st.rerun()
            with ct2:
                if peut_bloquer_users:
                    if st.button("🔄 Réinitialiser Tentatives", use_container_width=True):
                        db.q('UPDATE utilisateurs SET tentatives_connexion=0')
                        st.success("✅ Tentatives réinitialisées!")

    with admin_tabs[8]:
        st.markdown("<h2 style='color:#f39c12;'>📢 Panneau Maintenance</h2>", unsafe_allow_html=True)
        if not est_admin_principal:
            st.warning("🔒 Réservé à l'administrateur principal.")
        else:
            maint_data = db.f1("SELECT * FROM maintenance ORDER BY id DESC LIMIT 1")
            est_actif = (maint_data.get('actif', 0) == 1) if maint_data else False
            msg_actuel = maint_data.get('message', '') if maint_data else ''

            cm1, cm2 = st.columns([1, 3])
            with cm1:
                if est_actif:
                    st.markdown("<div style='background:#f39c12;color:white;padding:20px;border-radius:12px;text-align:center;font-weight:700;'>🔧 EN MAINTENANCE</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='background:#27ae60;color:white;padding:20px;border-radius:12px;text-align:center;font-weight:700;'>✅ EN LIGNE</div>", unsafe_allow_html=True)
            with cm2:
                if msg_actuel:
                    st.info(f"📢 Message actuel: **{msg_actuel}**")
                else:
                    st.caption("Aucun message configuré")

            st.divider()
            with st.form("form_maintenance_panel", border=False):
                nouveau_msg = st.text_area("✏️ Message affiché aux utilisateurs",
                    value=msg_actuel, height=120)
                cb1, cb2 = st.columns(2)
                with cb1:
                    lbl = "🔧 Activer Maintenance" if not est_actif else "✅ Désactiver"
                    btn_toggle = st.form_submit_button(lbl, use_container_width=True, type="primary")
                with cb2:
                    btn_save = st.form_submit_button("💾 Sauvegarder message", use_container_width=True)

                if btn_toggle:
                    if not est_actif and not nouveau_msg.strip():
                        st.error("❌ Écrivez un message avant d'activer!")
                    else:
                        nouvel_etat = 0 if est_actif else 1
                        if maint_data:
                            db.q("UPDATE maintenance SET actif=?, message=?, updated_at=NOW() WHERE id=?",
                                (nouvel_etat, nouveau_msg, maint_data['id']))
                        else:
                            db.q("INSERT INTO maintenance (actif, message) VALUES (?, ?)",
                                (nouvel_etat, nouveau_msg))
                        st.success("✅ État modifié!")
                        st.rerun()
                if btn_save:
                    if maint_data:
                        db.q("UPDATE maintenance SET message=? WHERE id=?", (nouveau_msg, maint_data['id']))
                    else:
                        db.q("INSERT INTO maintenance (actif, message) VALUES (0, ?)", (nouveau_msg,))
                    st.success("💾 Message sauvegardé!")
                    st.rerun()

    with admin_tabs[9]:
        st.subheader("💬 Feedbacks des Apprenants")
        feedbacks = db.fa('SELECT * FROM feedback ORDER BY date_feedback DESC')
        if feedbacks:
            for fb in feedbacks:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class="card">
                        <strong>{fb['titre']}</strong> - {fb['type']}<br>
                        <small>📧 {safe(fb,'email')}</small><br>
                        <p style="margin-top:10px;">{fb['message']}</p>
                        <small style="color:#999;">📅 {fb['date_feedback']}</small>
                    </div>""", unsafe_allow_html=True)
                with col2:
                    if peut_supprimer:
                        if st.button("🗑️", key=f"feedback_del_{fb['id']}", use_container_width=True):
                            db.q('DELETE FROM feedback WHERE id=?', (fb['id'],))
                            st.rerun()
                    else:
                        st.markdown("<small style='color:#999;'>🔒</small>", unsafe_allow_html=True)
        else:
            st.info("ℹ️ Aucun feedback")

    with admin_tabs[10]:
        st.subheader("💰 Gestion des Paiements")
        if not perms['gerer_paiements']:
            st.warning("🔒 Vous n'avez pas la permission de gérer les paiements.")
        else:
            paiements = db.fa("""SELECT p.*, u.nom, u.prenom, u.email, o.nom as offre_nom, o.duree_jours
                                 FROM paiements p
                                 LEFT JOIN utilisateurs u ON u.id = p.utilisateur_id
                                 LEFT JOIN offres o ON o.id = p.offre_id
                                 WHERE p.statut='en_attente'
                                 ORDER BY p.date_soumission DESC""")
            st.markdown(f"### ⏳ En attente ({len(paiements)})")
            if not paiements:
                st.success("✅ Aucun paiement en attente")
            for p in paiements:
                with st.expander(f"💳 {safe(p,'prenom')} {safe(p,'nom')} — {p['montant']} FCFA — réf: {p['reference']}"):
                    ci, ca = st.columns([2, 1])
                    with ci:
                        st.markdown(f"""
                        - **Utilisateur :** {safe(p,'prenom')} {safe(p,'nom')} ({safe(p,'email')})
                        - **Offre :** {safe(p,'offre_nom')} ({safe(p,'duree_jours','?')} jours)
                        - **Montant :** {p['montant']} FCFA
                        - **Référence :** `{p['reference']}`
                        - **Notes :** {p.get('notes') or '—'}
                        - **Soumis :** {p['date_soumission']}
                        """)
                    with ca:
                        if st.button("✅ Valider", key=f"valider_{p['id']}",
                                    use_container_width=True, type="primary"):
                            prolonger_abo(p['utilisateur_id'], p['duree_jours'])
                            db.q("""UPDATE paiements SET statut='valide',
                                    date_validation=NOW(), valide_par=%s WHERE id=%s""",
                                (st.session_state.user.get('email','?'), p['id']))
                            st.success(f"✅ Paiement validé — {p['duree_jours']} jours ajoutés")
                            st.rerun()
                        if st.button("❌ Rejeter", key=f"rejeter_{p['id']}", use_container_width=True):
                            db.q("UPDATE paiements SET statut='rejete' WHERE id=%s", (p['id'],))
                            st.warning("Paiement rejeté")
                            st.rerun()

            st.divider()
            st.markdown("### 📜 Historique")
            historique = db.fa("""SELECT p.*, u.prenom, u.nom FROM paiements p
                                  LEFT JOIN utilisateurs u ON u.id = p.utilisateur_id
                                  WHERE p.statut IN ('valide','rejete')
                                  ORDER BY p.date_validation DESC LIMIT 20""")
            if historique:
                df_hist = pd.DataFrame([{
                    'Date': h.get('date_validation'),
                    'Utilisateur': f"{safe(h,'prenom')} {safe(h,'nom')}",
                    'Montant': h['montant'],
                    'Réf.': h['reference'],
                    'Statut': h['statut'],
                    'Validé par': h.get('valide_par') or '—'
                } for h in historique])
                st.dataframe(df_hist, use_container_width=True)
            else:
                st.caption("Aucun historique")

    with admin_tabs[11]:
        st.subheader("⚙️ Paramètres de la Plateforme")
        if not perms['gerer_parametres']:
            st.warning("🔒 Réservé à l'administrateur principal.")
        else:
            st.markdown("### 📱 Coordonnées de paiement")
            om = db.f1("SELECT valeur FROM parametres WHERE cle='orange_money_numero'") or {'valeur':''}
            wa = db.f1("SELECT valeur FROM parametres WHERE cle='whatsapp_numero'") or {'valeur':''}
            ca, cb = st.columns(2)
            with ca: new_om = st.text_input("Numéro Orange Money", value=om['valeur'])
            with cb: new_wa = st.text_input("Numéro WhatsApp", value=wa['valeur'])
            if st.button("💾 Enregistrer les coordonnées", type="primary"):
                db.q("UPDATE parametres SET valeur=%s, updated_at=NOW() WHERE cle='orange_money_numero'", (new_om,))
                db.q("UPDATE parametres SET valeur=%s, updated_at=NOW() WHERE cle='whatsapp_numero'", (new_wa,))
                st.success("✅ Enregistré")
                st.rerun()

            st.divider()
            st.markdown("### ⏱️ Durée essai gratuit")
            duree = db.f1("SELECT valeur FROM parametres WHERE cle='duree_essai_jours'") or {'valeur':'14'}
            try:
                duree_val = int(duree['valeur'] or 14)
            except Exception:
                duree_val = 14
            new_duree = st.number_input("Jours d'essai pour nouveaux comptes",
                                        min_value=0, max_value=90, value=duree_val)
            if st.button("💾 Enregistrer la durée"):
                db.q("UPDATE parametres SET valeur=%s WHERE cle='duree_essai_jours'", (str(new_duree),))
                st.success("✅ Durée mise à jour")
                st.rerun()

            st.divider()
            st.markdown("### 💎 Offres d'abonnement")
            with st.form("form_add_offre", border=False):
                c1, c2, c3, c4 = st.columns(4)
                with c1: n_nom = st.text_input("Nom", placeholder="1 mois")
                with c2: n_montant = st.number_input("Montant (FCFA)", min_value=0, step=500, value=2000)
                with c3: n_duree = st.number_input("Durée (jours)", min_value=1, value=30)
                with c4:
                    st.write(""); st.write("")
                    submit_offre = st.form_submit_button("➕ Ajouter", use_container_width=True, type="primary")
                if submit_offre and n_nom:
                    db.q('INSERT INTO offres (nom,montant,duree_jours) VALUES (?,?,?)',
                         (n_nom, n_montant, n_duree))
                    st.success("✅ Offre ajoutée")
                    st.rerun()

            st.markdown("#### Offres actuelles")
            for o in db.fa('SELECT * FROM offres ORDER BY montant'):
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                with c1: st.markdown(f"**{o['nom']}**")
                with c2: st.markdown(f"{o['montant']} FCFA")
                with c3: st.markdown(f"{o['duree_jours']} jours")
                with c4:
                    if st.button("🗑️", key=f"del_offre_{o['id']}"):
                        db.q("DELETE FROM offres WHERE id=%s", (o['id'],))
                        st.rerun()

    st.write("---")
    if st.button("🚪 Déconnexion Admin", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v if not isinstance(v, (dict, list)) else type(v)()
        st.session_state.page = "home"
        st.rerun()
