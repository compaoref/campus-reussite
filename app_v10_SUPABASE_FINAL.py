"""
🎓 CAMPUS RÉUSSITE v10 - ULTRA SÉCURISÉE
✅ BD persistante sur disque (data/campus_persistant.db)
✅ Effacement auto des champs après création
✅ Interface de maintenance (débloquer comptes, stats)
✅ Permissions admin secondaire (pas de suppression ni ajout admin)
✅ Blocage compte après 3 tentatives de connexion
✅ Détection capture d'écran (blocage session)
✅ Aucune sélection par défaut dans les quiz
"""

import streamlit as st
import pandas as pd
import json
import hashlib
from datetime import datetime, timedelta
import os
from base64 import b64encode

st.set_page_config(
    page_title="Campus Réussite v10",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# BD PERSISTANTE sur disque
os.makedirs("data", exist_ok=True)
DB_PATH = "data/campus_persistant.db"  # Persistant 24/7!

# ========== CONFIGURATION LOGO ==========
# À modifier: mettez l'URL ou le chemin de votre logo
LOGO_URL = "logo.png"  # Votre logo local

# ========== CSS EXTRAORDINAIRE ==========
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
    
    /* LOGO STYLING */
    .logo-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
        animation: fadeInDown 0.8s ease-out;
    }
    
    .logo-container img {
        height: 120px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .logo-container img:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* HEADER PROFESSIONNEL */
    .header-main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        text-align: center;
        animation: slideInUp 0.8s ease-out;
    }
    
    .header-main h1 {
        font-size: 2.8em;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-main p {
        font-size: 1.15em;
        opacity: 0.95;
        font-weight: 300;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* CARD QUIZ */
    .card-quiz {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 35px;
        border-radius: 18px;
        margin: 20px 0;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        border: 2px solid transparent;
    }
    
    .card-quiz:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4);
        border: 2px solid rgba(255,255,255,0.3);
    }
    
    .card-quiz-title {
        font-size: 1.6em;
        font-weight: 700;
        margin: 15px 0;
        color: white;
    }
    
    .card-quiz-desc {
        font-size: 1em;
        color: rgba(255,255,255,0.9);
        margin-bottom: 15px;
        line-height: 1.5;
    }
    
    .card-quiz-count {
        font-size: 1.4em;
        color: rgba(255,255,255,0.95);
        font-weight: 700;
        padding-top: 15px;
        border-top: 2px solid rgba(255,255,255,0.2);
    }
    
    /* QUESTION BOX */
    .question-box {
        background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
        padding: 30px;
        border-radius: 15px;
        margin: 25px 0;
        border-left: 6px solid #667eea;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
        animation: fadeIn 0.6s ease-out;
    }
    
    .question-number {
        font-size: 0.9em;
        color: #667eea;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    
    .question-text {
        font-size: 1.5em;
        color: #1a1a1a;
        font-weight: 700;
        margin-bottom: 25px;
        line-height: 1.6;
    }
    
    /* PROGRESS BAR */
    .progress-container {
        margin: 30px 0;
        padding: 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .progress-bar {
        width: 100%;
        height: 12px;
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin-top: 10px;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.4s ease;
        border-radius: 10px;
    }
    
    /* CORRECTION PAGE */
    .correction-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
        animation: slideInDown 0.8s ease-out;
    }
    
    .correction-header h2 {
        font-size: 2.2em;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    /* SCORE DISPLAY */
    .score-display {
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
        color: white;
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        margin: 30px 0;
        box-shadow: 0 10px 30px rgba(52, 211, 153, 0.3);
        animation: zoomIn 0.6s ease-out;
    }
    
    .score-big {
        font-size: 4em;
        font-weight: 700;
        margin: 20px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .score-percentage {
        font-size: 2.5em;
        font-weight: 700;
        margin: 15px 0;
        opacity: 0.95;
    }
    
    .score-message {
        font-size: 1.3em;
        margin-top: 15px;
        font-weight: 500;
    }
    
    .score-display.orange {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }
    
    .score-display.red {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    }
    
    @keyframes zoomIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* CORRECTION ITEM */
    .correction-item {
        background: white;
        padding: 30px;
        margin: 20px 0;
        border-radius: 15px;
        border-left: 6px solid #e0e0e0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.4s ease;
        animation: slideInLeft 0.6s ease-out;
    }
    
    .correction-item.correct {
        border-left-color: #10b981;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(16, 185, 129, 0.02) 100%);
    }
    
    .correction-item.incorrect {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(239, 68, 68, 0.02) 100%);
    }
    
    .correction-item:hover {
        transform: translateX(10px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .correction-question {
        font-size: 1.3em;
        font-weight: 700;
        margin-bottom: 20px;
        color: #1a1a1a;
    }
    
    .correction-status {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 700;
        margin-bottom: 15px;
        font-size: 0.95em;
    }
    
    .correction-status.correct {
        background: #d1fae5;
        color: #065f46;
    }
    
    .correction-status.incorrect {
        background: #fee2e2;
        color: #7f1d1d;
    }
    
    .correction-row {
        margin: 15px 0;
        padding: 12px;
        background: white;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .correction-row.user {
        border-left: 4px solid #3b82f6;
    }
    
    .correction-row.correct-answer {
        border-left: 4px solid #10b981;
    }
    
    .correction-label {
        font-weight: 700;
        color: #667eea;
        min-width: 150px;
        font-size: 0.95em;
    }
    
    .correction-text {
        flex: 1;
        color: #1a1a1a;
        font-size: 1.05em;
    }
    
    .correction-explication {
        background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
        border-left: 4px solid #667eea;
        font-style: italic;
        color: #333;
        line-height: 1.6;
    }
    
    .explication-label {
        font-weight: 700;
        color: #667eea;
        margin-bottom: 10px;
    }
    
    /* ICON STYLING */
    .status-icon {
        font-size: 2em;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    /* BUTTONS */
    .btn-custom {
        padding: 15px 35px;
        font-size: 1.05em;
        font-weight: 700;
        border-radius: 12px;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .btn-primary:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .btn-secondary {
        background: white;
        color: #667eea;
        border: 2px solid #667eea;
    }
    
    .btn-secondary:hover {
        background: #f0f4ff;
    }
    
    /* TIMEOUT INDICATOR */
    .timeout-indicator {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-weight: 700;
        z-index: 1000;
        border: 2px solid #667eea;
    }
    
    .timeout-green {
        color: #10b981;
        border-color: #10b981;
    }
    
    .timeout-orange {
        color: #f59e0b;
        border-color: #f59e0b;
        animation: blink 1s infinite;
    }
    
    .timeout-red {
        color: #ef4444;
        border-color: #ef4444;
        animation: blink 0.5s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* FADE IN ANIMATION */
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* RESULT SUMMARY */
    .result-summary {
        background: white;
        padding: 30px;
        border-radius: 15px;
        margin: 30px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .summary-title {
        font-size: 1.5em;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .summary-stats {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-top: 20px;
    }
    
    .stat-item {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
        border-radius: 10px;
    }
    
    .stat-label {
        color: #667eea;
        font-weight: 700;
        font-size: 0.95em;
        margin-bottom: 10px;
    }
    
    .stat-value {
        font-size: 2em;
        font-weight: 700;
        color: #1a1a1a;
    }
    
    /* BACKGROUND AVEC LOGO */
    .logo-background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('logo.png');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        opacity: 0.06;
        z-index: -1;
        pointer-events: none;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
        z-index: 10;
    }
    
    .logo-container img {
        max-width: 180px;
        height: auto;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    /* TABLEAU ADMIN */
    .admin-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .admin-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        text-align: left;
        font-weight: 700;
    }
    
    .admin-table td {
        padding: 15px;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .admin-table tr:hover {
        background: #f5f5f5;
    }
    
    /* CARD ADMIN */
    .admin-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
    }
    
    .admin-card h3 {
        color: #667eea;
        margin-bottom: 15px;
    }
    
    /* STAT BOX ADMIN */
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 15px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
        min-width: 150px;
    }
    
    .stat-box-number {
        font-size: 2.5em;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .stat-box-label {
        font-size: 0.95em;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ========== DATABASE CLASS - SUPABASE + CONNECTION POOL ==========
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
    st.markdown("### Format URL correct")
    st.code('DATABASE_URL = "postgresql://postgres.XXXX:MOTDEPASSE@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"', language="toml")
    if st.button("Rafraichir pour retenter", type="primary", use_container_width=True):
        st.rerun()
    st.stop()


@st.cache_resource
def get_pool(url: str):
    """
    Crée UN SEUL pool de connexions pour toute la session Streamlit.
    st.cache_resource garantit qu'il est créé une seule fois et réutilisé.
    minconn=1, maxconn=5 — suffisant pour une app Streamlit.
    """
    try:
        p = pg_pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=5,
            dsn=url,
            sslmode="require",
            connect_timeout=10,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
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
            _show_db_error_page(
                "Lecture DATABASE_URL",
                "Clé DATABASE_URL introuvable dans Settings → Secrets.",
                "AUCUNE URL"
            )
        url = st.secrets["DATABASE_URL"]
        if not url or not url.startswith("postgresql"):
            _show_db_error_page("Format URL", f"L'URL doit commencer par 'postgresql'.\nActuel: {url[:40]}", url[:40])
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
        """Emprunte une connexion du pool"""
        try:
            return self._pool.getconn()
        except Exception as e:
            _show_db_error_page("Connexion pool", str(e), self._masquer_url())

    def _release(self, conn):
        """Remet la connexion dans le pool"""
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
                """CREATE TABLE IF NOT EXISTS series (
                    id SERIAL PRIMARY KEY, nom TEXT UNIQUE,
                    description TEXT, nombre_questions INTEGER DEFAULT 0)""",
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
            ]
            for sql in tables:
                c.execute(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            _show_db_error_page("Création des tables", str(e), self._masquer_url())
        finally:
            self._release(conn)

    def q(self, sql, p=()):
        """INSERT / UPDATE / DELETE — retourne True/False"""
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
        """Retourne une seule ligne (dict)"""
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
        """Retourne toutes les lignes (liste de dicts)"""
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

def hash_pwd(p):
    return hashlib.sha256((p + "salt2024").encode()).hexdigest()

def verify_pwd(p, h):
    return hash_pwd(p) == h

def safe(obj, key, defaut="N/A"):
    """Accès sécurisé à un dict — retourne defaut si obj est None ou clé absente"""
    if obj is None:
        return defaut
    try:
        val = obj.get(key, defaut) if isinstance(obj, dict) else getattr(obj, key, defaut)
        return val if val is not None else defaut
    except Exception:
        return defaut

# ========== SESSION MANAGEMENT ==========
def check_session_timeout():
    if not st.session_state.logged_in or not st.session_state.user or st.session_state.is_admin:
        return
    try:
        user = db.f1('SELECT * FROM utilisateurs WHERE id=?', (st.session_state.user['id'],))
        if not user:
            return
        
        last_activity = user.get('last_activity')
        
        # Si last_activity est None ou vide, mettre à jour et continuer
        if not last_activity:
            db.q('UPDATE utilisateurs SET last_activity=NOW() WHERE id=?',
                (user['id'],))
            return
        
        # Convertir en datetime selon le type reçu
        if isinstance(last_activity, datetime):
            dt = last_activity.replace(tzinfo=None)
        elif isinstance(last_activity, str):
            # Nettoyer le string et parser
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
        # En cas d'erreur, ne pas bloquer la connexion
        pass

def update_activity():
    if st.session_state.logged_in and st.session_state.user and not st.session_state.is_admin:
        try:
            db.q('UPDATE utilisateurs SET last_activity=NOW() WHERE id=?',
                (st.session_state.user['id'],))
        except Exception:
            pass

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
            'version': '9.2'
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
if "correction_data" not in st.session_state:
    st.session_state.correction_data = None
# ✅ COMPTEURS DE CLÉS pour vider les formulaires automatiquement
if "register_form_key" not in st.session_state:
    st.session_state.register_form_key = 0
if "quiz_form_key" not in st.session_state:
    st.session_state.quiz_form_key = 0
if "serie_form_key" not in st.session_state:
    st.session_state.serie_form_key = 0
if "admin_form_key" not in st.session_state:
    st.session_state.admin_form_key = 0

check_session_timeout()
update_activity()

# ========== HELPER FUNCTIONS ==========
def display_logo():
    """Affiche le logo de manière dynamique et professionnelle"""
    import os
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo.png", width=180, use_column_width=False)
    
    # Ajouter le background du logo
    st.markdown("""
    <div class="logo-background"></div>
    """, unsafe_allow_html=True)

def get_score_color(percentage):
    """Retourne la couleur basée sur le pourcentage"""
    if percentage >= 80:
        return "green", "🎉 Excellent travail!", "#34d399"
    elif percentage >= 60:
        return "orange", "👍 Bon travail!", "#f59e0b"
    else:
        return "red", "💪 Continuez vos efforts!", "#ef4444"

def display_correction(quizzes, quiz_answers, serie):
    """Affiche les corrections de manière spectaculaire et dynamique"""
    
    score = 0
    details = []
    
    # Calculer le score et collecter les détails
    for q in quizzes:
        user_answer = quiz_answers.get(q['id'], 'Non répondu')
        correct_answers = q['reponses_correctes'].split(",")
        is_correct = user_answer in correct_answers
        
        if is_correct:
            score += 1
        
        details.append({
            'question': q['question'],
            'user_answer': user_answer,
            'correct_answers': correct_answers,
            'option_a': q['option_a'],
            'option_b': q['option_b'],
            'option_c': q['option_c'],
            'option_d': q['option_d'],
            'explication': q['explication'],
            'is_correct': is_correct,
            'options_dict': {
                'A': q['option_a'],
                'B': q['option_b'],
                'C': q['option_c'],
                'D': q['option_d']
            }
        })
    
    percentage = (score / len(quizzes)) * 100
    color_type, message, color_code = get_score_color(percentage)
    
    # HEADER DES CORRECTIONS
    st.markdown(f"""
    <div class="correction-header">
        <h2>📋 Votre Correction Détaillée</h2>
        <p>{serie['nom']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # SCORE SPECTACULAIRE
    score_class = "score-display" if percentage >= 80 else "score-display orange" if percentage >= 60 else "score-display red"
    
    st.markdown(f"""
    <div class="{score_class}">
        <h2>✨ Quiz Complété!</h2>
        <div class="score-big">{score}/{len(quizzes)}</div>
        <div class="score-percentage">{percentage:.1f}%</div>
        <div class="score-message">{message}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # RÉSUMÉ STATISTIQUE
    st.markdown(f"""
    <div class="result-summary">
        <div class="summary-title">📊 Résumé de Votre Performance</div>
        <div class="summary-stats">
            <div class="stat-item">
                <div class="stat-label">✅ Bonnes réponses</div>
                <div class="stat-value" style="color: #10b981;">{score}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">❌ Mauvaises réponses</div>
                <div class="stat-value" style="color: #ef4444;">{len(quizzes) - score}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">📈 Pourcentage</div>
                <div class="stat-value" style="color: #667eea;">{percentage:.1f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # CORRECTIONS DÉTAILLÉES - NOUVELLE VERSION MAGNIFIQUE
    st.markdown("<h3 style='color: #1a1a1a; font-size: 1.8em; margin: 40px 0 30px 0; font-weight: 700;'>🔍 Détail de Vos Réponses</h3>", unsafe_allow_html=True)
    
    for idx, detail in enumerate(details, 1):
        is_correct = detail['is_correct']
        status_badge = "✅ CORRECT" if is_correct else "❌ INCORRECT"
        badge_bg = "#d1fae5" if is_correct else "#fee2e2"
        badge_color = "#065f46" if is_correct else "#7f1d1d"
        border_color = "#10b981" if is_correct else "#ef4444"
        
        # QUESTION HEADER
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
            border-left: 6px solid {border_color};
            padding: 25px;
            border-radius: 12px;
            margin: 20px 0 15px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        ">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div style="font-weight: 700; color: #667eea; font-size: 1em;">Question {idx}/{len(details)}</div>
                <div style="
                    background: {badge_bg};
                    color: {badge_color};
                    padding: 6px 16px;
                    border-radius: 20px;
                    font-weight: 700;
                    font-size: 0.9em;
                ">{status_badge}</div>
            </div>
            <div style="font-size: 1.3em; font-weight: 700; color: #1a1a1a; line-height: 1.6;">
                {detail['question']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # COLONNES: VOTRE RÉPONSE ET BONNE RÉPONSE
        col1, col2 = st.columns(2)
        
        # VOTRE RÉPONSE
        with col1:
            if detail['user_answer'] != 'Non répondu':
                user_option_text = detail['options_dict'].get(detail['user_answer'], 'Non trouvé')
                border = "#ef4444" if not is_correct else "#10b981"
                bg = "#fff5f5" if not is_correct else "#f0fdf4"
                
                st.markdown(f"""
                <div style="
                    background: {bg};
                    border-left: 5px solid {border};
                    padding: 20px;
                    border-radius: 8px;
                    margin: 15px 0;
                ">
                    <div style="color: #667eea; font-weight: 700; margin-bottom: 10px; font-size: 0.95em;">👤 Votre réponse</div>
                    <div style="
                        background: white;
                        padding: 15px;
                        border-radius: 6px;
                        border-left: 4px solid {border};
                        font-weight: 600;
                        color: #1a1a1a;
                    ">
                        <span style="font-size: 1.1em; font-weight: 700; color: {border};">{detail['user_answer']}</span>) {user_option_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: #fff5f5;
                    border-left: 5px solid #ef4444;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 15px 0;
                ">
                    <div style="color: #667eea; font-weight: 700; margin-bottom: 10px; font-size: 0.95em;">👤 Votre réponse</div>
                    <div style="
                        background: white;
                        padding: 15px;
                        border-radius: 6px;
                        color: #ef4444;
                        font-weight: 700;
                    ">
                        Non répondu
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # BONNE RÉPONSE
        with col2:
            for correct_ans in detail['correct_answers']:
                correct_option_text = detail['options_dict'].get(correct_ans, 'Non trouvé')
                st.markdown(f"""
                <div style="
                    background: #f0fdf4;
                    border-left: 5px solid #10b981;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 15px 0;
                ">
                    <div style="color: #667eea; font-weight: 700; margin-bottom: 10px; font-size: 0.95em;">✅ Bonne réponse</div>
                    <div style="
                        background: white;
                        padding: 15px;
                        border-radius: 6px;
                        border-left: 4px solid #10b981;
                        font-weight: 600;
                        color: #1a1a1a;
                    ">
                        <span style="font-size: 1.1em; font-weight: 700; color: #10b981;">{correct_ans}</span>) {correct_option_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # EXPLICATION EN PLEINE LARGEUR
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            padding: 25px;
            border-radius: 10px;
            margin: 20px 0 30px 0;
            border-left: 5px solid #f59e0b;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15);
        ">
            <div style="
                font-weight: 700;
                color: #92400e;
                margin-bottom: 12px;
                font-size: 1.05em;
            ">💡 Explication</div>
            <div style="
                color: #78350f;
                line-height: 1.7;
                font-size: 1em;
            ">
                {detail['explication']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return score, percentage

# ========== BANNIERE MAINTENANCE ==========
def afficher_banniere_maintenance():
    try:
        maint = db.f1("SELECT * FROM maintenance ORDER BY id DESC LIMIT 1")
        if maint and maint.get('actif', 0) == 1 and maint.get('message', '').strip():
            msg = maint['message']
            st.markdown(
                "<div style='background:linear-gradient(135deg,#f39c12,#e67e22);color:white;"
                "padding:18px 24px;border-radius:12px;margin-bottom:20px;text-align:center;"
                "font-size:1rem;font-weight:700;box-shadow:0 4px 15px rgba(243,156,18,0.4);'>"
                f"&#x1F527; <b>Maintenance en cours</b> &mdash; {msg}"
                "</div>",
                unsafe_allow_html=True
            )
    except Exception:
        pass

afficher_banniere_maintenance()

# ========== LOGIN PAGE ==========
if not st.session_state.logged_in:
    
    # Logo en haut
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
                admin = db.f1("SELECT * FROM admins WHERE email=? AND status='actif'", (email.lower(),))
                if admin and verify_pwd(pwd, admin['password_hash']):
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.user = admin
                    st.success("✅ Connexion Admin réussie!")
                    st.rerun()
                
                # Vérifier Apprenant
                user = db.f1('SELECT * FROM utilisateurs WHERE email=?', (email.lower(),))
                if user:
                    # Vérifier si le compte est bloqué
                    if user.get('bloque', 0) == 1:
                        st.error(f"🚫 Compte bloqué: {user.get('raison_blocage', 'Contactez l\'admin')}")
                    elif user.get('status') == 'bloqué':
                        st.error("❌ Votre compte a été suspendu par l\'administrateur")
                    elif user.get('tentatives_connexion', 0) >= 3:
                        # Bloquer automatiquement
                        db.q('UPDATE utilisateurs SET bloque=1, date_blocage=?, raison_blocage=? WHERE id=?',
                            (datetime.now().isoformat(), "3 tentatives de connexion échouées", user['id']))
                        st.error("🚫 Compte bloqué après 3 tentatives. Contactez l\'administrateur.")
                    elif verify_pwd(pwd, user['password_hash']):
                        # Succès - réinitialiser tentatives
                        db.q('UPDATE utilisateurs SET tentatives_connexion=0, last_activity=NOW() WHERE id=?',
                            (user['id'],))
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.is_admin = False
                        st.success("✅ Bienvenue!")
                        st.rerun()
                    else:
                        # Échec - incrémenter tentatives
                        new_t = user.get('tentatives_connexion', 0) + 1
                        db.q('UPDATE utilisateurs SET tentatives_connexion=? WHERE id=?', (new_t, user['id']))
                        reste = max(0, 3 - new_t)
                        if reste > 0:
                            st.error(f"❌ Mot de passe incorrect. Il vous reste {reste} tentative(s).")
                        else:
                            db.q('UPDATE utilisateurs SET bloque=1, date_blocage=?, raison_blocage=? WHERE id=?',
                                (datetime.now().isoformat(), "3 tentatives de connexion échouées", user['id']))
                            st.error("🚫 Compte bloqué après 3 tentatives. Contactez l\'administrateur.")
                else:
                    st.error("❌ Email ou mot de passe incorrect")
        
        with tab2:
            st.subheader("📝 Créer un nouveau compte")
            
            # Formulaire avec clé dynamique → vide à chaque succès
            with st.form(key=f"register_form_{st.session_state.register_form_key}", border=False):
                col_nom, col_prenom = st.columns(2)
                with col_nom:
                    nom = st.text_input("👤 Nom", placeholder="Votre nom de famille")
                with col_prenom:
                    prenom = st.text_input("👤 Prénom", placeholder="Votre prénom")
                
                email = st.text_input("📧 Adresse email", placeholder="exemple@email.com")
                password = st.text_input("🔑 Mot de passe (min 6 caractères)", type="password", placeholder="Minimum 6 caractères")
                pwd_confirm = st.text_input("🔑 Confirmer le mot de passe", type="password", placeholder="Répétez le mot de passe")
                
                st.info("💡 Utilisez votre email pour vous connecter par la suite")
                
                submitted = st.form_submit_button("✨ S'inscrire", use_container_width=True, type="primary")
                
                if submitted:
                    if not nom or not prenom or not email or not password:
                        st.error("❌ Remplissez tous les champs")
                    elif len(password) < 6:
                        st.error("❌ Mot de passe trop court (minimum 6 caractères)")
                    elif password != pwd_confirm:
                        st.error("❌ Les mots de passe ne correspondent pas")
                    else:
                        result = db.q('INSERT INTO utilisateurs (nom,prenom,email,password_hash) VALUES (?,?,?,?)',
                            (nom, prenom, email.lower(), hash_pwd(password)))
                        if result:
                            st.success("✅ Compte créé! Vous pouvez en créer un autre ou vous connecter.")
                            # ✅ Incrémenter la clé → formulaire complètement vide!
                            st.session_state.register_form_key += 1
                            st.rerun()
                        else:
                            st.error("❌ Cet email est déjà utilisé")

# ========== APPRENANT INTERFACE ==========
elif st.session_state.logged_in and not st.session_state.is_admin:
    
    # Logo en haut
    display_logo()
    
    # Header
    st.markdown(f"""
    <div class="header-main">
        <h1>👋 Bienvenue {safe(st.session_state.user,'prenom','Apprenant')}!</h1>
        <p>Continuez votre apprentissage et progressez</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Timeout indicator
    user = db.f1('SELECT * FROM utilisateurs WHERE id=?', (st.session_state.user['id'],))
    if user:
        try:
            last_activity = user.get('last_activity')
            if last_activity:
                if isinstance(last_activity, datetime):
                    dt = last_activity.replace(tzinfo=None)
                elif isinstance(last_activity, str):
                    last_activity = last_activity.split('.')[0].replace('T', ' ').strip()
                    dt = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
                else:
                    dt = datetime.now()
                
                elapsed = int((datetime.now() - dt).total_seconds() / 60)
                timeout = user.get('session_minutes', 120) or 120
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
        except Exception:
            pass
    
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
                        <div style="font-size: 3em;">📚</div>
                        <div class="card-quiz-title">{safe(s,'nom')}</div>
                        <div class="card-quiz-desc">{s['description']}</div>
                        <div class="card-quiz-count">🎯 {len(quizzes)} questions</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Commencer {s['nom']}", key=f"quiz_{s['id']}", use_container_width=True):
                        st.session_state.page = f"quiz_{s['id']}"
                        st.session_state.current_series_id = s['id']
                        st.session_state.current_quizzes = quizzes
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.rerun()
        else:
            st.info("ℹ️ Aucun quiz disponible pour le moment. Revenez bientôt!")
        
        # Quiz Display
        for s in series:
            if st.session_state.page == f"quiz_{s['id']}" and st.session_state.current_quizzes:
                quizzes = st.session_state.current_quizzes
                
                st.markdown(f"""
                <div class="header-main" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-align: center;">
                    <h2>📖 {s['nom']}</h2>
                    <p>{s['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if quizzes:
                    # Progress bar
                    progress = len(st.session_state.quiz_answers) / len(quizzes)
                    st.markdown(f"""
                    <div class="progress-container">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="font-weight: 700; color: #667eea;">Progression: {int(progress*100)}%</span>
                            <span style="color: #999;">{len(st.session_state.quiz_answers)}/{len(quizzes)} répondu(e)s</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {progress*100}%"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("")
                    
                    # Questions
                    for idx, q in enumerate(quizzes, 1):
                        st.markdown(f"""
                        <div class="question-box">
                            <div class="question-number">Question {idx}/{len(quizzes)}</div>
                            <div class="question-text">{q['question']}</div>
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
                            label_visibility="collapsed",
                            index=None
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
                            st.session_state.current_quizzes = []
                            st.rerun()
                    
                    with col2:
                        if st.button("✅ Soumettre les réponses", use_container_width=True, type="primary"):
                            # Vérifier que TOUTES les questions ont une réponse
                            unanswered = []
                            for idx, q in enumerate(quizzes, 1):
                                if q['id'] not in st.session_state.quiz_answers or st.session_state.quiz_answers[q['id']] is None:
                                    unanswered.append(idx)
                            
                            if unanswered:
                                st.error(f"❌ Vous n'avez pas répondu aux questions: {', '.join(map(str, unanswered))}")
                                st.stop()
                            
                            # Sauvegarder le résultat
                            score = 0
                            for q in quizzes:
                                if q['id'] in st.session_state.quiz_answers and st.session_state.quiz_answers[q['id']] is not None:
                                    if st.session_state.quiz_answers[q['id']] in q['reponses_correctes'].split(","):
                                        score += 1
                            
                            percentage = (score / len(quizzes)) * 100
                            db.q('INSERT INTO resultats (utilisateur_id,series_id,score,total,pourcentage) VALUES (?,?,?,?,?)',
                                (st.session_state.user['id'], s['id'], score, len(quizzes), percentage))
                            
                            st.session_state.quiz_submitted = True
                            st.session_state.current_series_id = s['id']
                            st.rerun()
                
                # Results Page - AFFICHAGE DES CORRECTIONS
                if st.session_state.quiz_submitted and st.session_state.current_series_id == s['id']:
                    score, percentage = display_correction(quizzes, st.session_state.quiz_answers, s)
                    
                    st.write("")
                    st.write("---")
                    st.write("")
                    
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
                            st.session_state.current_quizzes = []
                            st.rerun()
    
    # ========== TAB 2: RÉSULTATS ==========
    with tab2:
        st.subheader("📊 Votre historique de résultats")
        
        resultats = db.fa('SELECT * FROM resultats WHERE utilisateur_id=? ORDER BY date_test DESC', 
                          (st.session_state.user['id'],))
        
        if resultats:
            for res in resultats:
                serie = db.f1('SELECT * FROM series WHERE id=?', (res['series_id'],))
                # Protection si la série a été supprimée directement en BD
                nom_serie = safe(serie, 'nom', 'Série supprimée')
                
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
                            <h3>{emoji} {nom_serie}</h3>
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
    
    # Logo en haut
    display_logo()
    
    st.markdown("""
    <div class="header-main">
        <h1>🔐 Panneau d'Administration</h1>
        <p>Gestion complète de la plateforme</p>
    </div>
    """, unsafe_allow_html=True)
    
    # JS anti-capture d'écran
    st.markdown("""
    <script>
    document.addEventListener('keyup', function(e) {
        if (e.key === 'PrintScreen') {
            window.parent.postMessage({type: 'screenshot_attempt'}, '*');
            alert('⚠️ Les captures d\'écran sont interdites sur cette plateforme!');
        }
    });
    document.addEventListener('keydown', function(e) {
        if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === '3' || e.key === '4' || e.key === 'S')) {
            e.preventDefault();
            alert('⚠️ Les captures d\'écran sont interdites sur cette plateforme!');
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Récupérer les permissions de l'admin connecté
    admin_connecte = db.f1("SELECT * FROM admins WHERE email=?", (st.session_state.user.get('email',''),)) if st.session_state.user.get('id', 0) != 0 else None
    est_admin_principal = st.session_state.user.get('id', 0) == 0 or (admin_connecte and admin_connecte.get('niveau_permission') == 'principal')
    peut_supprimer       = est_admin_principal or (admin_connecte and admin_connecte.get('peut_supprimer_quiz', 0) == 1)
    peut_ajouter_admin   = est_admin_principal or (admin_connecte and admin_connecte.get('peut_ajouter_admin', 0) == 1)
    peut_bloquer_users   = est_admin_principal or (admin_connecte and admin_connecte.get('peut_bloquer_users', 0) == 1)
    peut_suppr_users     = est_admin_principal or (admin_connecte and admin_connecte.get('peut_supprimer_users', 0) == 1)
    peut_suppr_admins    = est_admin_principal or (admin_connecte and admin_connecte.get('peut_supprimer_admins', 0) == 1)
    
    if not est_admin_principal:
        st.warning("ℹ️ Vous êtes connecté en tant qu'administrateur secondaire — certaines fonctionnalités sont restreintes.")
    
    # Admin Menu
    admin_tabs = st.tabs([
        "📊 Dashboard",
        "📚 Séries",
        "🎯 Quizzes",
        "📤 Importer",
        "👥 Apprenants",
        "👨‍💼 Administrateurs",
        "💾 Base Données",
        "🔧 Maintenance",
        "📢 Panneau Maintenance",
        "💬 Feedback"
    ])
    
    # ========== DASHBOARD ==========
    with admin_tabs[0]:
        st.markdown("<h2 style='color: #667eea; margin-bottom: 30px;'>📊 Tableaux de Bord</h2>", unsafe_allow_html=True)
        
        # STATISTIQUES PRINCIPALES
        col1, col2, col3, col4 = st.columns(4)
        
        users_count = len(db.fa('SELECT * FROM utilisateurs'))
        series_count = len(db.fa('SELECT * FROM series'))
        quizzes_count = len(db.fa('SELECT * FROM quiz'))
        feedback_count = len(db.fa('SELECT * FROM feedback'))
        
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-box-label">👥 Apprenants</div>
                <div class="stat-box-number">{users_count}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-box-label">📚 Séries</div>
                <div class="stat-box-number">{series_count}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-box-label">🎯 Quizzes</div>
                <div class="stat-box-number">{quizzes_count}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-box-label">💬 Feedbacks</div>
                <div class="stat-box-number">{feedback_count}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # ACTIVITÉ RÉCENTE
        st.markdown("<h3 style='color: #667eea; margin-top: 30px;'>📈 Activité Récente</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # Résultats récents
        with col1:
            st.markdown("<h4 style='color: #1a1a1a;'>Tests Récents</h4>", unsafe_allow_html=True)
            resultats_recents = db.fa('SELECT * FROM resultats ORDER BY date_test DESC LIMIT 5')
            if resultats_recents:
                for res in resultats_recents:
                    user = db.f1('SELECT * FROM utilisateurs WHERE id=?', (res['utilisateur_id'],))
                    serie = db.f1('SELECT * FROM series WHERE id=?', (res['series_id'],))
                    # Protection si user ou serie supprimés directement en BD
                    if not user or not serie:
                        continue
                    emoji = "🎉" if res['pourcentage'] >= 80 else "👍" if res['pourcentage'] >= 60 else "💪"
                    st.markdown(f"""
                    <div class="admin-card">
                        <strong>{emoji} {safe(user,'prenom')} {safe(user,'nom')}</strong><br>
                        {safe(serie,'nom')}<br>
                        <span style="color: #667eea; font-weight: 700;">{res['pourcentage']:.1f}% ({res['score']}/{res['total']})</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun test effectué")
        
        # Utilisateurs actifs
        with col2:
            st.markdown("<h4 style='color: #1a1a1a;'>Utilisateurs Actifs</h4>", unsafe_allow_html=True)
            users = db.fa('SELECT * FROM utilisateurs ORDER BY last_activity DESC LIMIT 5')
            if users:
                for user in users:
                    if not user:
                        continue
                    st.markdown(f"""
                    <div class="admin-card">
                        <strong>{safe(user,'prenom')} {safe(user,'nom')}</strong><br>
                        <span style="color: #666; font-size: 0.9em;">{safe(user,'email')}</span><br>
                        <span style="color: #10b981; font-weight: 700;">{'🟢 Actif' if safe(user,'status') == 'actif' else '🔴 Bloqué'}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun utilisateur")
    
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
                if st.button("🗑️ Supprimer", key=f"serie_del_{s['id']}", use_container_width=True):
                    db.q('DELETE FROM quiz WHERE series_id=?', (s['id'],))
                    db.q('DELETE FROM series WHERE id=?', (s['id'],))
                    st.success("✅ Série supprimée")
                    st.rerun()
    
    # ========== QUIZZES ==========
    with admin_tabs[2]:
        st.markdown("<h2 style='color: #667eea;'>🎯 Gestion des Quizzes</h2>", unsafe_allow_html=True)
        
        series = db.fa('SELECT * FROM series')
        if not series:
            st.warning("⚠️ Créez d'abord une série!")
        else:
            # ONGLETS: VOIR ou CRÉER
            sub_tab1, sub_tab2 = st.tabs(["📋 Voir Quizzes", "➕ Créer Manuelle"])
            
            # VOIR LES QUIZZES
            with sub_tab1:
                selected_series = st.selectbox(
                    "Sélectionner une série",
                    [(s['id'], s['nom']) for s in series],
                    format_func=lambda x: x[1],
                    key="view_series"
                )
                
                st.divider()
                quizzes = db.fa('SELECT * FROM quiz WHERE series_id=?', (selected_series[0],))
                
                st.markdown(f"<h4>📚 {len(quizzes)} quizzes</h4>", unsafe_allow_html=True)
                
                if quizzes:
                    # AFFICHAGE AVEC CARTES ET BOUTONS
                    for idx, q in enumerate(quizzes, 1):
                        col1, col2, col3 = st.columns([3, 0.5, 0.5])
                        
                        with col1:
                            st.markdown(f"""
                            <div class="admin-card">
                                <strong>Q{idx}: {q['question']}</strong>
                                <div style="margin-top: 15px; color: #666;">
                                    <small>
                                        A) {q['option_a']}<br>
                                        B) {q['option_b']}<br>
                                        C) {q['option_c']}<br>
                                        D) {q['option_d']}
                                    </small>
                                </div>
                                <div style="margin-top: 10px;">
                                    <span style="color: #667eea; font-weight: 700; font-size: 0.9em;">✅ Réponse(s): {q['reponses_correctes']}</span>
                                </div>
                                <div style="margin-top: 10px;">
                                    <small style="color: #999;">💡 {q['explication'][:80]}...</small>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
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
                        
                        # Édition inline
                        if st.session_state.editing_quiz_id == q['id']:
                            st.divider()
                            st.markdown(f"### ✏️ Éditer Q{idx}")
                            
                            with st.form(f"edit_form_{q['id']}", border=False):
                                new_q = st.text_area("Question", value=q['question'], height=80)
                                
                                col_a, col_b, col_c, col_d = st.columns(4)
                                with col_a:
                                    new_a = st.text_input("Option A", value=q['option_a'])
                                with col_b:
                                    new_b = st.text_input("Option B", value=q['option_b'])
                                with col_c:
                                    new_c = st.text_input("Option C", value=q['option_c'])
                                with col_d:
                                    new_d = st.text_input("Option D", value=q['option_d'])
                                
                                new_correct = st.multiselect(
                                    "Réponses correctes",
                                    ["A", "B", "C", "D"],
                                    default=q['reponses_correctes'].split(",")
                                )
                                
                                new_expl = st.text_area("Explication", value=q['explication'], height=80)
                                
                                col_save, col_cancel = st.columns(2)
                                with col_save:
                                    if st.form_submit_button("💾 Sauvegarder", use_container_width=True, type="primary"):
                                        db.q('UPDATE quiz SET question=?,option_a=?,option_b=?,option_c=?,option_d=?,reponses_correctes=?,explication=? WHERE id=?',
                                            (new_q, new_a, new_b, new_c, new_d, ",".join(new_correct), new_expl, q['id']))
                                        st.success("✅ Quiz modifié!")
                                        st.session_state.editing_quiz_id = None
                                        st.rerun()
                                
                                with col_cancel:
                                    if st.form_submit_button("❌ Annuler", use_container_width=True):
                                        st.session_state.editing_quiz_id = None
                                        st.rerun()
                else:
                    st.info("Aucun quiz dans cette série")
            
            # CRÉER MANUELLE
            with sub_tab2:
                st.markdown("<h4 style='color: #667eea;'>➕ Créer un nouveau Quiz</h4>", unsafe_allow_html=True)
                
                selected_series_create = st.selectbox(
                    "Sélectionner la série",
                    [(s['id'], s['nom']) for s in series],
                    format_func=lambda x: x[1],
                    key="create_series"
                )
                
                with st.form(f"create_quiz_form_{st.session_state.quiz_form_key}", border=False):
                    st.markdown("<h5>Informations du Quiz</h5>", unsafe_allow_html=True)
                    
                    question = st.text_area("📝 Question", height=100, placeholder="Écrivez la question ici...")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        option_a = st.text_input("Option A)", placeholder="Première réponse")
                    with col2:
                        option_b = st.text_input("Option B)", placeholder="Deuxième réponse")
                    with col3:
                        option_c = st.text_input("Option C)", placeholder="Troisième réponse")
                    with col4:
                        option_d = st.text_input("Option D)", placeholder="Quatrième réponse")
                    
                    st.divider()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        reponses_correctes = st.multiselect(
                            "✅ Sélectionner la/les bonne(s) réponse(s)",
                            ["A", "B", "C", "D"],
                            default=[]
                        )
                    
                    with col2:
                        st.write("")
                        st.write("")
                        if st.checkbox("Réponses multiples?", value=False):
                            st.caption("✅ Les apprenants devront trouver TOUTES les bonnes réponses")
                    
                    explication = st.text_area("💡 Explication (optionnel)", height=80, placeholder="Expliquez pourquoi c'est la bonne réponse...")
                    
                    st.divider()
                    
                    submitted = st.form_submit_button("✅ Créer le Quiz", use_container_width=True, type="primary")
                    
                    if submitted:
                        if question and option_a and option_b and option_c and option_d and reponses_correctes:
                            reponses_str = ",".join(reponses_correctes)
                            if db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)',
                                (selected_series_create[0], question, option_a, option_b, option_c, option_d, reponses_str, explication)):
                                st.success("✅ Quiz créé! Les champs sont vidés, vous pouvez en créer un autre.")
                                st.balloons()
                                # ✅ Incrémenter la clé → formulaire complètement vide!
                                st.session_state.quiz_form_key += 1
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la création")
                        else:
                            st.error("❌ Remplissez tous les champs obligatoires (question, options A-D et réponse correcte)")
    
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
            active = len([u for u in users if u and safe(u,'status') == 'actif'])
            st.markdown(f'<div class="stat-box"><div style="font-size: 0.9em;">Actifs</div><div class="stat-number">{active}</div></div>', unsafe_allow_html=True)
        with col3:
            blocked = len([u for u in users if u and safe(u,'status') == 'bloqué'])
            st.markdown(f'<div class="stat-box"><div style="font-size: 0.9em;">Bloqués</div><div class="stat-number">{blocked}</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        
        for u in users:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                if not u: continue
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
                new_dur = st.number_input("Min", 5, 1440, u['session_minutes'], 
                                         key=f"apprenant_dur_{u['id']}", step=1)
                if new_dur != u['session_minutes']:
                    db.q('UPDATE utilisateurs SET session_minutes=? WHERE id=?', (new_dur, u['id']))
                    st.rerun()
            
            with col4:
                if peut_suppr_users:
                    if st.button("🗑️ Supprimer", key=f"apprenant_del_{u['id']}", use_container_width=True):
                        db.q('DELETE FROM utilisateurs WHERE id=?', (u['id'],))
                        st.rerun()
                else:
                    st.markdown("<small style='color:#999;'>🔒 Non autorisé</small>", unsafe_allow_html=True)
            
            st.divider()
    
    # ========== ADMINISTRATEURS ==========
    with admin_tabs[5]:
        st.subheader("👨‍💼 Gestion des Administrateurs")
        
        if peut_ajouter_admin:
            with st.form(f"create_admin_form_{st.session_state.admin_form_key}", border=False):
                st.markdown("#### ➕ Créer un nouvel administrateur")
                col_a, col_b = st.columns(2)
                with col_a:
                    nom_admin    = st.text_input("Nom *")
                    email_admin  = st.text_input("Email *")
                    pwd_admin    = st.text_input("Mot de passe (min 8 car.) *", type="password")
                with col_b:
                    prenom_admin     = st.text_input("Prénom *")
                    pwd_admin_confirm = st.text_input("Confirmer le mot de passe *", type="password")
                
                st.markdown("---")
                st.markdown("#### 🔐 Accès autorisés")
                st.caption("Cochez uniquement ce que cet admin peut faire")
                
                pc1, pc2, pc3 = st.columns(3)
                with pc1:
                    p_quiz_add  = st.checkbox("➕ Ajouter des quiz",     value=True)
                    p_quiz_imp  = st.checkbox("📥 Importer des quiz",    value=True)
                    p_quiz_del  = st.checkbox("🗑️ Supprimer des quiz",   value=False)
                with pc2:
                    p_user_view = st.checkbox("👁️ Voir les apprenants",  value=True)
                    p_user_blk  = st.checkbox("🔒 Bloquer/Débloquer apprenants", value=False)
                    p_user_del  = st.checkbox("🗑️ Supprimer apprenants", value=False)
                with pc3:
                    p_adm_add   = st.checkbox("👨‍💼 Ajouter des admins",  value=False)
                    p_adm_del   = st.checkbox("🗑️ Supprimer des admins", value=False)
                    p_maintenance = st.checkbox("🔧 Gérer la maintenance", value=False)
                
                submitted_admin = st.form_submit_button("✅ Créer l'administrateur", use_container_width=True, type="primary")
                
                if submitted_admin:
                    if len(pwd_admin) < 8:
                        st.error("❌ Mot de passe trop court (minimum 8 caractères)")
                    elif pwd_admin != pwd_admin_confirm:
                        st.error("❌ Les mots de passe ne correspondent pas")
                    elif not all([nom_admin, prenom_admin, email_admin]):
                        st.error("❌ Remplissez tous les champs obligatoires (*)")
                    else:
                        ok = db.q(
                            'INSERT INTO admins (email,password_hash,nom,prenom,niveau_permission,'
                            'peut_supprimer_quiz,peut_ajouter_admin,peut_bloquer_users,'
                            'peut_supprimer_users,peut_supprimer_admins) VALUES (?,?,?,?,?,?,?,?,?,?)',
                            (email_admin.lower(), hash_pwd(pwd_admin), nom_admin, prenom_admin,
                             'secondaire',
                             1 if p_quiz_del  else 0,
                             1 if p_adm_add   else 0,
                             1 if p_user_blk  else 0,
                             1 if p_user_del  else 0,
                             1 if p_adm_del   else 0)
                        )
                        if ok:
                            st.success(f"✅ Admin créé avec succès: {email_admin}")
                            st.session_state.admin_form_key += 1
                            st.rerun()
                        else:
                            st.error("❌ Cet email est déjà utilisé")
        else:
            st.warning("🔒 Vous n'avez pas la permission d'ajouter des administrateurs.")
        
        st.write("---")
        st.subheader("Administrateurs actuels")
        
        admins = db.fa('SELECT * FROM admins')
        for admin in admins:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if not admin: continue
                icon = "✅" if safe(admin,'status') == 'actif' else "🔒"
                st.markdown(f"**{icon} {safe(admin,'prenom')} {safe(admin,'nom')}**")
                st.caption(f"📧 {safe(admin,'email')}")
            
            with col2:
                if est_admin_principal:
                    if st.button("🔒" if safe(admin,'status') == 'actif' else "✅", 
                                key=f"admin_block_{admin['id']}", use_container_width=True):
                        new_status = 'bloqué' if safe(admin,'status') == 'actif' else 'actif'
                        db.q('UPDATE admins SET status=? WHERE id=?', (new_status, admin['id']))
                        st.rerun()
                else:
                    st.markdown("<small style='color:#999;'>🔒 Non autorisé</small>", unsafe_allow_html=True)
            
            with col3:
                if peut_suppr_admins:
                    if st.button("🗑️", key=f"admin_del_{admin['id']}", use_container_width=True):
                        db.q('DELETE FROM admins WHERE id=?', (admin['id'],))
                        st.rerun()
                else:
                    st.markdown("<small style='color:#999;'>🔒</small>", unsafe_allow_html=True)
            
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
    
    # ========== MAINTENANCE ==========
    with admin_tabs[8]:
        st.markdown("<h2 style='color:#f39c12;'>📢 Panneau Maintenance Plateforme</h2>", unsafe_allow_html=True)
        st.markdown("Activez la maintenance et écrivez un message visible par **tous les utilisateurs** sur la plateforme.")
        st.divider()
        
        maint_data = db.f1("SELECT * FROM maintenance ORDER BY id DESC LIMIT 1")
        est_actif  = (maint_data.get('actif', 0) == 1) if maint_data else False
        msg_actuel = maint_data.get('message', '') if maint_data else ''
        
        col_m1, col_m2 = st.columns([1, 3])
        with col_m1:
            if est_actif:
                st.markdown("<div style='background:#f39c12;color:white;padding:20px;border-radius:12px;text-align:center;font-weight:700;font-size:1.1em;'>🔧 EN MAINTENANCE</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='background:#27ae60;color:white;padding:20px;border-radius:12px;text-align:center;font-weight:700;font-size:1.1em;'>✅ EN LIGNE</div>", unsafe_allow_html=True)
        with col_m2:
            if msg_actuel:
                st.info(f"📢 Message actuel: **{msg_actuel}**")
            else:
                st.caption("Aucun message configuré")
        
        st.divider()
        
        with st.form("form_maintenance_panel", border=False):
            nouveau_msg = st.text_area(
                "✏️ Message affiché aux utilisateurs",
                value=msg_actuel, height=120,
                placeholder="Ex: Plateforme en maintenance pour amélioration. Revenez dans 30 minutes. Merci!"
            )
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                lbl = "🔧 Activer Maintenance" if not est_actif else "✅ Désactiver Maintenance"
                btn_toggle = st.form_submit_button(lbl, use_container_width=True, type="primary")
            with col_b2:
                btn_save = st.form_submit_button("💾 Sauvegarder message", use_container_width=True)
            
            if btn_toggle:
                if not est_actif and not nouveau_msg.strip():
                    st.error("❌ Écrivez un message avant d'activer la maintenance!")
                else:
                    nouvel_etat = 0 if est_actif else 1
                    if maint_data:
                        db.q("UPDATE maintenance SET actif=?, message=?, updated_at=NOW() WHERE id=?",
                            (nouvel_etat, nouveau_msg, maint_data['id']))
                    else:
                        db.q("INSERT INTO maintenance (actif, message) VALUES (?, ?)", (nouvel_etat, nouveau_msg))
                    if nouvel_etat == 1:
                        st.success("🔧 Maintenance ACTIVÉE — message visible pour tous!")
                    else:
                        st.success("✅ Maintenance DÉSACTIVÉE — plateforme en ligne!")
                    st.rerun()
            
            if btn_save:
                if maint_data:
                    db.q("UPDATE maintenance SET message=? WHERE id=?", (nouveau_msg, maint_data['id']))
                else:
                    db.q("INSERT INTO maintenance (actif, message) VALUES (0, ?)", (nouveau_msg,))
                st.success("💾 Message sauvegardé!")
                st.rerun()

    with admin_tabs[7]:
        st.markdown("<h2 style='color: #667eea;'>🔧 Interface de Maintenance</h2>", unsafe_allow_html=True)
        
        maint_t1, maint_t2, maint_t3 = st.tabs(["🚫 Comptes Bloqués", "📊 Statistiques BD", "⚙️ Outils"])
        
        with maint_t1:
            st.markdown("<h3>Comptes bloqués</h3>", unsafe_allow_html=True)
            blocked = db.fa('SELECT * FROM utilisateurs WHERE bloque=1')
            if blocked:
                for bu in blocked:
                    col_b1, col_b2 = st.columns([3, 1])
                    with col_b1:
                        st.markdown(f"""
                        <div class="admin-card" style="background:#ffe0e0; border-left-color: #ef4444;">
                            <strong>🚫 {safe(bu,'prenom')} {safe(bu,'nom')}</strong><br>
                            📧 {safe(bu,'email')}<br>
                            ❌ Raison: {bu.get('raison_blocage', 'N/A')}<br>
                            📅 {bu.get('date_blocage', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b2:
                        if st.button("🔓 Débloquer", key=f"unblock_{bu['id']}", use_container_width=True):
                            db.q('UPDATE utilisateurs SET bloque=0, tentatives_connexion=0, raison_blocage=NULL WHERE id=?', (bu['id'],))
                            st.success(f"✅ {safe(bu,'prenom')} débloqué!")
                            st.rerun()
            else:
                st.success("✅ Aucun compte bloqué en ce moment")
        
        with maint_t2:
            st.markdown("<h3>Statistiques en Temps Réel</h3>", unsafe_allow_html=True)
            m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
            stats_vals = [
                ("👥", "Utilisateurs", len(db.fa('SELECT id FROM utilisateurs'))),
                ("👨‍💼", "Admins", len(db.fa('SELECT id FROM admins'))),
                ("📚", "Séries", len(db.fa('SELECT id FROM series'))),
                ("🎯", "Quizzes", len(db.fa('SELECT id FROM quiz'))),
                ("🚫", "Bloqués", len(db.fa('SELECT id FROM utilisateurs WHERE bloque=1')))
            ]
            for col_m, (emoji, label, val) in zip([m_col1, m_col2, m_col3, m_col4, m_col5], stats_vals):
                with col_m:
                    st.markdown(f'<div class="stat-box"><div class="stat-box-label">{emoji} {label}</div><div class="stat-box-number">{val}</div></div>', unsafe_allow_html=True)
            st.divider()
            if os.path.exists(DB_PATH):
                size_kb = os.path.getsize(DB_PATH) / 1024
                st.info(f"📁 Fichier BD: {size_kb:.1f} KB — {DB_PATH}")
        
        with maint_t3:
            st.markdown("<h3>Outils Système</h3>", unsafe_allow_html=True)
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                if st.button("🔓 Débloquer TOUS les comptes", use_container_width=True):
                    db.q('UPDATE utilisateurs SET bloque=0, tentatives_connexion=0')
                    st.success("✅ Tous les comptes débloqués!")
                    st.rerun()
            with col_t2:
                if st.button("🔄 Réinitialiser Tentatives", use_container_width=True):
                    db.q('UPDATE utilisateurs SET tentatives_connexion=0')
                    st.success("✅ Tentatives réinitialisées!")
    
    # ========== FEEDBACK ==========
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
                        <p style="margin-top: 10px;">{fb['message']}</p>
                        <small style="color: #999;">📅 {fb['date_feedback']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("🗑️", key=f"feedback_del_{fb['id']}", use_container_width=True):
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
