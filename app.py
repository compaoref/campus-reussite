"""
🎓 CAMPUS RÉUSSITE v8.3 - FINAL & STABLE
Inscription + Connexion robuste, Dashboard admin complet
"""

import streamlit as st
import sqlite3
import pandas as pd
import re
import os
import hashlib
from datetime import datetime, timedelta

st.set_page_config(page_title="Campus Réussite", layout="wide")

DB_PATH = "campus.db"

# ========== DATABASE ==========
class DB:
    def __init__(self):
        self.init()
    
    def init(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY, nom TEXT, prenom TEXT, email TEXT UNIQUE,
            username TEXT UNIQUE, password_hash TEXT, role TEXT DEFAULT 'apprenant',
            status TEXT DEFAULT 'actif', session_minutes INTEGER DEFAULT 120)''')
        c.execute('''CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY, nom TEXT UNIQUE, description TEXT, nombre_questions INTEGER DEFAULT 50)''')
        c.execute('''CREATE TABLE IF NOT EXISTS quiz (
            id INTEGER PRIMARY KEY, series_id INTEGER, question TEXT, option_a TEXT,
            option_b TEXT, option_c TEXT, option_d TEXT, reponses_correctes TEXT, explication TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS quiz_pending (
            id INTEGER PRIMARY KEY, question TEXT, option_a TEXT, option_b TEXT,
            option_c TEXT, option_d TEXT, reponses_correctes TEXT, explication TEXT, categorie TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS resultats (
            id INTEGER PRIMARY KEY, utilisateur_id INTEGER, series_id INTEGER,
            score INTEGER, total INTEGER, pourcentage REAL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY, email TEXT, titre TEXT, message TEXT, type TEXT)''')
        conn.commit()
        conn.close()
    
    def q(self, sql, p=()):
        conn = sqlite3.connect(DB_PATH)
        conn.execute(sql, p)
        conn.commit()
        conn.close()
    
    def f1(self, sql, p=()):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        r = conn.execute(sql, p).fetchone()
        conn.close()
        return dict(r) if r else None
    
    def fa(self, sql, p=()):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        r = conn.execute(sql, p).fetchall()
        conn.close()
        return [dict(x) for x in r]

db = DB()

def hash_pwd(p):
    return hashlib.sha256((p + "salt2024").encode()).hexdigest()

def verify_pwd(p, h):
    return hash_pwd(p) == h

def add_user(n, pn, e, u, p):
    e = e.lower()
    if db.f1('SELECT id FROM utilisateurs WHERE email=?', (e,)):
        return False, "email"
    if db.f1('SELECT id FROM utilisateurs WHERE username=?', (u,)):
        return False, "user"
    try:
        db.q('INSERT INTO utilisateurs (nom,prenom,email,username,password_hash) VALUES (?,?,?,?,?)',
            (n, pn, e, u, hash_pwd(p)))
        return True, "ok"
    except:
        return False, "err"

def get_user(e):
    return db.f1('SELECT * FROM utilisateurs WHERE email=?', (e.lower(),))

# ========== INIT SESSION STATE ==========
for key in ["logged_in", "is_admin", "user", "page", "admin_tab", "email_prefill", "pwd_prefill"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["user"] else (False if key in ["logged_in", "is_admin"] else "")

st.markdown("""<style>
.header {background: linear-gradient(135deg, #1a5f3d 0%, #d4a574 100%);
color:white; padding:20px; border-radius:15px; text-align:center; margin-bottom:20px;}
.stat {background: linear-gradient(135deg, #1a5f3d 0%, #d4a574 100%); color:white;
padding:15px; border-radius:10px; text-align:center;}
</style>""", unsafe_allow_html=True)

# ========== LOGIN PAGE ==========
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="header"><h1>🎓 Campus Réussite</h1></div>', unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with t1:
            st.subheader("Connexion")
            email = st.text_input("Email", value=st.session_state.email_prefill or "")
            pwd = st.text_input("Mot de passe", type="password", value=st.session_state.pwd_prefill or "")
            
            if st.button("Se Connecter", use_container_width=True, type="primary"):
                try:
                    admins = st.secrets.get("admins", {})
                    if email.lower() in admins and admins[email.lower()] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.session_state.user = {'nom':'Admin','prenom':'Campus','email':email.lower(),'id':0}
                        st.rerun()
                except: pass
                
                user = get_user(email)
                if user and verify_pwd(pwd, user['password_hash']) and user['status']=='actif':
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.is_admin = False
                    st.session_state.email_prefill = ""
                    st.session_state.pwd_prefill = ""
                    st.rerun()
                else:
                    st.error("❌ Email ou mot de passe incorrect")
        
        with t2:
            st.subheader("Créer un Compte")
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email", key="reg_email")
            username = st.text_input("Username")
            password = st.text_input("Mot de passe", type="password", key="reg_pwd")
            pwd_confirm = st.text_input("Confirmer", type="password", key="reg_confirm")
            
            if st.button("S'Inscrire", use_container_width=True, type="primary"):
                if not all([nom, prenom, email, username, password]):
                    st.error("❌ Remplissez tous les champs")
                elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                    st.error("❌ Email invalide")
                elif password != pwd_confirm:
                    st.error("❌ Mots de passe différents")
                else:
                    ok, msg = add_user(nom, prenom, email, username, password)
                    if ok:
                        st.success("✅ Compte créé!")
                        st.session_state.email_prefill = email.lower()
                        st.session_state.pwd_prefill = password
                        st.info("➡️ Allez à 'Connexion' et cliquez 'Se Connecter'")
                    elif msg == "email":
                        st.error("❌ Cet email existe déjà")
                    elif msg == "user":
                        st.error("❌ Ce username existe déjà")
                    else:
                        st.error("❌ Erreur lors de la création")

# ========== MAIN APP ==========
else:
    user = st.session_state.user
    
    st.markdown(f'<div class="header"><h1>🎓 Campus Réussite</h1><p>{"Admin" if st.session_state.is_admin else "Apprenant"}: {user["prenom"]} {user["nom"]}</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.write(f"👤 {user['prenom']} {user['nom']}")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.is_admin = False
            st.rerun()
    
    if not st.session_state.is_admin:
        # ========== APPRENANT ==========
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("🏠 Accueil", use_container_width=True):
                st.session_state.page = "accueil"
        with c2:
            if st.button("📚 Séries", use_container_width=True):
                st.session_state.page = "series"
        with c3:
            if st.button("📊 Résultats", use_container_width=True):
                st.session_state.page = "resultats"
        with c4:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.page = "feedback"
        
        st.divider()
        
        if st.session_state.page in [None, "accueil"]:
            st.subheader("🎯 Bienvenue")
            series = db.fa('SELECT * FROM series')
            res = db.fa('SELECT * FROM resultats WHERE utilisateur_id=?', (user['id'],))
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="stat"><div style="font-size:2.5rem;font-weight:700">{len(series)}</div><div>Séries</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat"><div style="font-size:2.5rem;font-weight:700">{len(res)}</div><div>Complétées</div></div>', unsafe_allow_html=True)
            with c3:
                pct = int((len(res)/len(series)*100)) if series else 0
                st.markdown(f'<div class="stat"><div style="font-size:2.5rem;font-weight:700">{pct}%</div><div>Progression</div></div>', unsafe_allow_html=True)
            
            st.divider()
            for s in series:
                r = db.f1('SELECT * FROM resultats WHERE utilisateur_id=? AND series_id=?', (user['id'], s['id']))
                st.write(f"**{s['nom']}** - {s['nombre_questions']} q. - {'✅ '+str(r['score'])+'/'+str(r['total']) if r else '⏳ À faire'}")
                if st.button("Commencer", key=f"s{s['id']}", use_container_width=True):
                    st.session_state.page = f"series_{s['id']}"
                    st.rerun()
                st.divider()
        
        elif st.session_state.page == "series":
            st.subheader("📚 Séries")
            for s in db.fa('SELECT * FROM series'):
                r = db.f1('SELECT * FROM resultats WHERE utilisateur_id=? AND series_id=?', (user['id'], s['id']))
                if r:
                    st.success(f"✅ {s['nom']}: {r['score']}/{r['total']}")
                else:
                    st.write(f"⏳ {s['nom']}")
                if st.button("Faire", key=f"btn{s['id']}", use_container_width=True):
                    st.session_state.page = f"series_{s['id']}"
                    st.rerun()
                st.divider()
        
        elif st.session_state.page == "resultats":
            st.subheader("📊 Résultats")
            res = db.fa('SELECT * FROM resultats WHERE utilisateur_id=?', (user['id'],))
            if res:
                st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
        
        elif st.session_state.page == "feedback":
            st.subheader("💬 Feedback")
            with st.form("f"):
                titre = st.text_input("Titre")
                msg = st.text_area("Message")
                if st.form_submit_button("Envoyer", use_container_width=True):
                    db.q('INSERT INTO feedback (email,titre,message,type) VALUES (?,?,?,?)',
                        (user['email'], titre, msg, "feedback"))
                    st.success("✅ Envoyé!")
    
    else:
        # ========== ADMIN ==========
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.admin_tab = "dash"
        with c2:
            if st.button("📚 Séries", use_container_width=True):
                st.session_state.admin_tab = "series"
        with c3:
            if st.button("📤 Importer", use_container_width=True):
                st.session_state.admin_tab = "import"
        with c4:
            if st.button("👥 Apprenants", use_container_width=True):
                st.session_state.admin_tab = "users"
        with c5:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.admin_tab = "feedback"
        
        st.divider()
        
        if st.session_state.admin_tab in [None, "dash"]:
            st.subheader("📊 Statistiques")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="stat"><div style="font-size:2.5rem;font-weight:700">{len(db.fa("SELECT * FROM utilisateurs WHERE role=\'apprenant\'"))}</div><div>Apprenants</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat"><div style="font-size:2.5rem;font-weight:700">{len(db.fa("SELECT * FROM series"))}</div><div>Séries</div></div>', unsafe_allow_html=True)
            with c3:
                total = sum(len(db.fa('SELECT * FROM quiz WHERE series_id=?', (s['id'],))) for s in db.fa('SELECT * FROM series'))
                st.markdown(f'<div class="stat"><div style="font-size:2.5rem;font-weight:700">{total}</div><div>Quizzes</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="stat"><div style="font-size:2.5rem;font-weight:700">{len(db.fa("SELECT * FROM feedback"))}</div><div>Feedbacks</div></div>', unsafe_allow_html=True)
        
        elif st.session_state.admin_tab == "series":
            st.subheader("📚 Séries")
            with st.expander("➕ Créer Série"):
                nom = st.text_input("Nom")
                desc = st.text_area("Description")
                if st.button("Créer", use_container_width=True):
                    db.q('INSERT INTO series (nom,description) VALUES (?,?)', (nom, desc))
                    st.success("✅")
            
            st.divider()
            st.subheader("➕ Ajouter Quiz")
            s = db.fa('SELECT * FROM series')
            if s:
                sel = st.selectbox("Série", [(x['id'], x['nom']) for x in s], format_func=lambda x: x[1])
                with st.form("q"):
                    q = st.text_input("Question")
                    a = st.text_input("A")
                    b = st.text_input("B")
                    c = st.text_input("C")
                    d = st.text_input("D")
                    correct = st.multiselect("Correctes", ["A", "B", "C", "D"])
                    exp = st.text_area("Explication")
                    if st.form_submit_button("Ajouter", use_container_width=True):
                        db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)',
                            (sel[0], q, a, b, c, d, ",".join(correct), exp))
                        st.success("✅")
        
        elif st.session_state.admin_tab == "import":
            st.subheader("📤 Importer Quizzes")
            uploaded = st.file_uploader("CSV", type=["csv"])
            if uploaded:
                df = pd.read_csv(uploaded, sep=";")
                st.success(f"✅ {len(df)} lignes")
                s = db.fa('SELECT * FROM series')
                if s:
                    sel = st.selectbox("Série", [(x['id'], x['nom']) for x in s], format_func=lambda x: x[1])
                    if st.button("Ajouter", use_container_width=True, type="primary"):
                        for _, row in df.iterrows():
                            db.q('INSERT INTO quiz_pending VALUES (NULL,?,?,?,?,?,?,?,?)',
                                (row['question'], row['a'], row['b'], row['c'], row['d'], row['reponses_correctes'], row['explication'], sel[1]))
                        st.success("✅ En attente d'approbation!")
            
            st.divider()
            st.subheader("✅ En Attente")
            pending = db.fa('SELECT * FROM quiz_pending')
            if pending:
                for idx, p in enumerate(pending):
                    st.write(f"**Q{idx+1}: {p['question']}**")
                    st.write(f"A) {p['option_a']} | B) {p['option_b']} | C) {p['option_c']} | D) {p['option_d']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Approuver", key=f"a{p['id']}"):
                            s = db.f1('SELECT id FROM series WHERE nom=?', (p['categorie'],))
                            if not s:
                                db.q('INSERT INTO series (nom) VALUES (?)', (p['categorie'],))
                                s = db.f1('SELECT id FROM series WHERE nom=?', (p['categorie'],))
                            db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)',
                                (s['id'], p['question'], p['option_a'], p['option_b'], p['option_c'], p['option_d'], p['reponses_correctes'], p['explication']))
                            db.q('DELETE FROM quiz_pending WHERE id=?', (p['id'],))
                            st.rerun()
                    with c2:
                        if st.button("❌ Rejeter", key=f"r{p['id']}"):
                            db.q('DELETE FROM quiz_pending WHERE id=?', (p['id'],))
                            st.rerun()
                    st.divider()
        
        elif st.session_state.admin_tab == "users":
            st.subheader("👥 Apprenants")
            users = db.fa('SELECT * FROM utilisateurs WHERE role="apprenant"')
            for u in users:
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    icon = "✅" if u['status'] == 'actif' else "🔒"
                    st.write(f"{icon} {u['prenom']} {u['nom']}")
                with c2:
                    if st.button("Block" if u['status']=='actif' else "Unblock", key=f"b{u['id']}"):
                        new = 'bloqué' if u['status']=='actif' else 'actif'
                        db.q('UPDATE utilisateurs SET status=? WHERE id=?', (new, u['id']))
                        st.rerun()
                with c3:
                    dur = st.number_input("Min", 5, 1440, u['session_minutes'], key=f"d{u['id']}")
                    if dur != u['session_minutes']:
                        db.q('UPDATE utilisateurs SET session_minutes=? WHERE id=?', (dur, u['id']))
                st.divider()
        
        elif st.session_state.admin_tab == "feedback":
            st.subheader("💬 Feedback")
            for f in db.fa('SELECT * FROM feedback'):
                st.write(f"**{f['titre']}**")
                st.write(f"📧 {f['email']}")
                st.write(f"Message: {f['message']}")
                st.divider()
