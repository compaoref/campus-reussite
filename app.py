"""
🎓 CAMPUS RÉUSSITE v8.4 - COMPLET & FONCTIONNEL
Inscription, Connexion, Quizzes, Dashboard Admin
"""

import streamlit as st
import sqlite3
import pandas as pd
import re
import hashlib

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
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(sql, p)
            conn.commit()
            conn.close()
        except:
            pass
    
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
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "admin_tab" not in st.session_state:
    st.session_state.admin_tab = "dash"
if "email_prefill" not in st.session_state:
    st.session_state.email_prefill = ""
if "pwd_prefill" not in st.session_state:
    st.session_state.pwd_prefill = ""
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

st.markdown("""<style>
.header {background: linear-gradient(135deg, #1a5f3d 0%, #d4a574 100%);
color:white; padding:20px; border-radius:15px; text-align:center; margin-bottom:20px;}
.stat {background: linear-gradient(135deg, #1a5f3d 0%, #d4a574 100%); color:white;
padding:15px; border-radius:10px; text-align:center; margin: 10px 0;}
</style>""", unsafe_allow_html=True)

# ========== LOGIN PAGE ==========
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="header"><h1>🎓 Campus Réussite</h1></div>', unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with t1:
            st.subheader("Connexion")
            email = st.text_input("Email", value=st.session_state.email_prefill)
            pwd = st.text_input("Mot de passe", type="password", value=st.session_state.pwd_prefill)
            
            if st.button("Se Connecter", use_container_width=True, type="primary"):
                try:
                    admins = st.secrets.get("admins", {})
                    if email.lower() in admins and admins[email.lower()] == pwd:
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.session_state.user = {'nom':'Admin','prenom':'Campus','email':email.lower(),'id':0}
                        st.rerun()
                except: 
                    pass
                
                user = get_user(email)
                if user and verify_pwd(pwd, user['password_hash']):
                    if user['status'] == 'bloqué':
                        st.error("❌ Votre compte a été bloqué")
                    else:
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
    
    st.markdown(f'<div class="header"><h1>🎓 Campus Réussite</h1><p>{"👮 Admin" if st.session_state.is_admin else "👨‍🎓 Apprenant"}: {user["prenom"]} {user["nom"]}</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.write(f"👤 {user['prenom']} {user['nom']}")
        st.write(f"📧 {user['email']}")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.is_admin = False
            st.session_state.page = "home"
            st.rerun()
    
    if not st.session_state.is_admin:
        # ========== APPRENANT MODE ==========
        
        # Navigation
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("🏠 Accueil", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
        with c2:
            if st.button("📚 Séries", use_container_width=True):
                st.session_state.page = "series"
                st.rerun()
        with c3:
            if st.button("📊 Résultats", use_container_width=True):
                st.session_state.page = "resultats"
                st.rerun()
        with c4:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.page = "feedback"
                st.rerun()
        
        st.divider()
        
        # HOME PAGE
        if st.session_state.page == "home":
            st.subheader("🎯 Bienvenue")
            series = db.fa('SELECT * FROM series')
            res = db.fa('SELECT * FROM resultats WHERE utilisateur_id=?', (user['id'],))
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="stat"><div style="font-size:2rem;font-weight:700">{len(series)}</div><div>Séries Disponibles</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat"><div style="font-size:2rem;font-weight:700">{len(res)}</div><div>Complétées</div></div>', unsafe_allow_html=True)
            with c3:
                pct = int((len(res)/len(series)*100)) if series else 0
                st.markdown(f'<div class="stat"><div style="font-size:2rem;font-weight:700">{pct}%</div><div>Progression</div></div>', unsafe_allow_html=True)
            
            st.divider()
            st.subheader("📚 Commencer une Série")
            
            for s in series:
                r = db.f1('SELECT * FROM resultats WHERE utilisateur_id=? AND series_id=?', (user['id'], s['id']))
                status = f"✅ Score: {r['score']}/{r['total']}" if r else "⏳ À faire"
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{s['nom']}** - {s['nombre_questions']} questions - {status}")
                with col2:
                    if st.button("Commencer", key=f"home_s{s['id']}", use_container_width=True):
                        st.session_state.page = f"quiz_{s['id']}"
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.rerun()
                st.divider()
        
        # SÉRIES PAGE
        elif st.session_state.page == "series":
            st.subheader("📚 Mes Séries")
            series = db.fa('SELECT * FROM series')
            res = db.fa('SELECT * FROM resultats WHERE utilisateur_id=?', (user['id'],))
            
            for s in series:
                r = db.f1('SELECT * FROM resultats WHERE utilisateur_id=? AND series_id=?', (user['id'], s['id']))
                st.markdown(f"**{s['nom']}** - {s['nombre_questions']} questions")
                st.markdown(f"_{s['description']}_")
                
                if r:
                    st.success(f"✅ Score: {r['score']}/{r['total']} ({r['pourcentage']:.1f}%)")
                else:
                    st.info("⏳ Non complétée")
                
                if st.button("Faire", key=f"series_s{s['id']}", use_container_width=True):
                    st.session_state.page = f"quiz_{s['id']}"
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.rerun()
                st.divider()
        
        # RÉSULTATS PAGE
        elif st.session_state.page == "resultats":
            st.subheader("📊 Mes Résultats")
            res = db.fa('SELECT * FROM resultats WHERE utilisateur_id=?', (user['id'],))
            
            if res:
                data = []
                for r in res:
                    s = db.f1('SELECT nom FROM series WHERE id=?', (r['series_id'],))
                    data.append({
                        'Série': s['nom'] if s else 'N/A',
                        'Score': f"{r['score']}/{r['total']}",
                        'Pourcentage': f"{r['pourcentage']:.1f}%"
                    })
                st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            else:
                st.info("Aucun résultat")
        
        # FEEDBACK PAGE
        elif st.session_state.page == "feedback":
            st.subheader("💬 Envoyer un Feedback")
            with st.form("feedback_form"):
                titre = st.text_input("Titre")
                msg = st.text_area("Message")
                if st.form_submit_button("Envoyer", use_container_width=True):
                    if titre and msg:
                        db.q('INSERT INTO feedback (email,titre,message,type) VALUES (?,?,?,?)',
                            (user['email'], titre, msg, "feedback"))
                        st.success("✅ Feedback enregistré!")
                    else:
                        st.error("❌ Remplissez tous les champs")
        
        # QUIZ PAGE
        elif st.session_state.page.startswith("quiz_"):
            series_id = int(st.session_state.page.split("_")[1])
            series = db.f1('SELECT * FROM series WHERE id=?', (series_id,))
            quizzes = db.fa('SELECT * FROM quiz WHERE series_id=?', (series_id,))
            
            if not series:
                st.error("❌ Série non trouvée")
            elif not quizzes:
                st.error("❌ Aucun quiz dans cette série")
            else:
                st.subheader(f"🎯 {series['nom']}")
                st.write(f"Nombre de questions: {len(quizzes)}")
                st.divider()
                
                # Afficher les questions
                for idx, quiz in enumerate(quizzes):
                    st.markdown(f"**Question {idx+1}/{len(quizzes)}: {quiz['question']}**")
                    
                    options = {
                        'A': quiz['option_a'],
                        'B': quiz['option_b'],
                        'C': quiz['option_c'],
                        'D': quiz['option_d']
                    }
                    
                    # Réponses sélectionnées
                    if quiz['id'] not in st.session_state.quiz_answers:
                        st.session_state.quiz_answers[quiz['id']] = []
                    
                    selected = st.multiselect(
                        "Sélectionnez la/les bonnes réponse(s):",
                        ['A', 'B', 'C', 'D'],
                        default=st.session_state.quiz_answers[quiz['id']],
                        key=f"q_{quiz['id']}"
                    )
                    
                    st.session_state.quiz_answers[quiz['id']] = selected
                    
                    st.divider()
                
                # Bouton Valider
                if st.button("✅ VALIDER LA SÉRIE", use_container_width=True, type="primary"):
                    if len(st.session_state.quiz_answers) != len(quizzes):
                        st.error("❌ Répondez à TOUTES les questions!")
                    else:
                        # Calculer le score
                        score = 0
                        corrections = {}
                        
                        for quiz in quizzes:
                            correct_answers = [x.strip() for x in quiz['reponses_correctes'].split(',')]
                            user_answers = st.session_state.quiz_answers.get(quiz['id'], [])
                            
                            if set(user_answers) == set(correct_answers):
                                score += 1
                            
                            corrections[quiz['id']] = {
                                'question': quiz['question'],
                                'user_answers': user_answers,
                                'correct_answers': correct_answers,
                                'is_correct': set(user_answers) == set(correct_answers),
                                'explication': quiz['explication']
                            }
                        
                        # Sauvegarder le résultat
                        pourcentage = (score / len(quizzes) * 100) if quizzes else 0
                        db.q('INSERT INTO resultats (utilisateur_id,series_id,score,total,pourcentage) VALUES (?,?,?,?,?)',
                            (user['id'], series_id, score, len(quizzes), pourcentage))
                        
                        st.session_state.quiz_submitted = True
                        st.session_state.quiz_corrections = corrections
                        st.session_state.quiz_score = score
                        st.session_state.quiz_total = len(quizzes)
                        
                        # Afficher le résultat
                        st.success(f"✅ SÉRIE COMPLÉTÉE!")
                        st.markdown(f"### 📊 Votre Score: {score}/{len(quizzes)} ({pourcentage:.1f}%)")
                        st.balloons()
                        
                        st.divider()
                        st.markdown("### 📝 Corrections")
                        
                        for idx, (qid, corr) in enumerate(corrections.items()):
                            with st.expander(f"Question {idx+1}: {corr['question']}"):
                                st.markdown(f"**Votre réponse:** {', '.join(corr['user_answers']) if corr['user_answers'] else 'Non répondue'}")
                                st.markdown(f"**Réponse correcte:** {', '.join(corr['correct_answers'])}")
                                
                                if corr['is_correct']:
                                    st.success("✅ Correct!")
                                else:
                                    st.error("❌ Incorrect")
                                
                                st.markdown(f"**Explication:** {corr['explication']}")
                        
                        st.divider()
                        if st.button("🏠 Retour à l'accueil", use_container_width=True):
                            st.session_state.page = "home"
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_submitted = False
                            st.rerun()
    
    else:
        # ========== ADMIN MODE ==========
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.admin_tab = "dash"
                st.rerun()
        with c2:
            if st.button("📚 Séries", use_container_width=True):
                st.session_state.admin_tab = "series"
                st.rerun()
        with c3:
            if st.button("📤 Importer", use_container_width=True):
                st.session_state.admin_tab = "import"
                st.rerun()
        with c4:
            if st.button("👥 Apprenants", use_container_width=True):
                st.session_state.admin_tab = "users"
                st.rerun()
        with c5:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.admin_tab = "feedback"
                st.rerun()
        
        st.divider()
        
        if st.session_state.admin_tab == "dash":
            st.subheader("📊 Statistiques")
            c1, c2, c3, c4 = st.columns(4)
            
            with c1:
                count = len(db.fa("SELECT * FROM utilisateurs WHERE role='apprenant'"))
                st.markdown(f'<div class="stat"><div style="font-size:2rem">{count}</div><div>Apprenants</div></div>', unsafe_allow_html=True)
            with c2:
                count = len(db.fa("SELECT * FROM series"))
                st.markdown(f'<div class="stat"><div style="font-size:2rem">{count}</div><div>Séries</div></div>', unsafe_allow_html=True)
            with c3:
                quizzes = db.fa("SELECT * FROM quiz")
                st.markdown(f'<div class="stat"><div style="font-size:2rem">{len(quizzes)}</div><div>Quizzes</div></div>', unsafe_allow_html=True)
            with c4:
                count = len(db.fa("SELECT * FROM feedback"))
                st.markdown(f'<div class="stat"><div style="font-size:2rem">{count}</div><div>Feedbacks</div></div>', unsafe_allow_html=True)
        
        elif st.session_state.admin_tab == "series":
            st.subheader("📚 Gestion Séries")
            
            with st.expander("➕ Créer une Série"):
                nom = st.text_input("Nom de la série")
                desc = st.text_area("Description")
                if st.button("Créer", use_container_width=True):
                    if nom:
                        db.q('INSERT INTO series (nom,description) VALUES (?,?)', (nom, desc))
                        st.success("✅ Série créée!")
                        st.rerun()
                    else:
                        st.error("❌ Entrez un nom")
            
            st.divider()
            st.subheader("➕ Ajouter un Quiz")
            series_list = db.fa('SELECT * FROM series')
            if series_list:
                sel_series = st.selectbox("Sélectionner la série", [(s['id'], s['nom']) for s in series_list], format_func=lambda x: x[1])
                
                with st.form("add_quiz_form"):
                    question = st.text_input("Question")
                    opt_a = st.text_input("Option A")
                    opt_b = st.text_input("Option B")
                    opt_c = st.text_input("Option C")
                    opt_d = st.text_input("Option D")
                    correct = st.multiselect("Sélectionnez les bonnes réponses", ["A", "B", "C", "D"])
                    explication = st.text_area("Explication")
                    
                    if st.form_submit_button("Ajouter", use_container_width=True):
                        if all([question, opt_a, opt_b, opt_c, opt_d, correct, explication]):
                            db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)',
                                (sel_series[0], question, opt_a, opt_b, opt_c, opt_d, ",".join(correct), explication))
                            st.success("✅ Quiz ajouté!")
                            st.rerun()
                        else:
                            st.error("❌ Remplissez tous les champs")
        
        elif st.session_state.admin_tab == "import":
            st.subheader("📤 Importer des Quizzes")
            
            uploaded_file = st.file_uploader("Uploader un fichier CSV", type=["csv"])
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file, sep=";")
                    st.success(f"✅ {len(df)} quizzes chargés")
                    st.dataframe(df, use_container_width=True)
                    
                    series_list = db.fa('SELECT * FROM series')
                    if series_list:
                        sel_series = st.selectbox("Ajouter à quelle série?", [(s['id'], s['nom']) for s in series_list], format_func=lambda x: x[1])
                        
                        if st.button("Ajouter à la série", use_container_width=True, type="primary"):
                            count = 0
                            for _, row in df.iterrows():
                                db.q('INSERT INTO quiz_pending (question,option_a,option_b,option_c,option_d,reponses_correctes,explication,categorie) VALUES (?,?,?,?,?,?,?,?)',
                                    (row['question'], row['a'], row['b'], row['c'], row['d'], row['reponses_correctes'], row['explication'], sel_series[1]))
                                count += 1
                            st.success(f"✅ {count} quizzes en attente d'approbation!")
                            st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
            
            st.divider()
            st.subheader("✅ Quizzes en Attente d'Approbation")
            
            pending = db.fa('SELECT * FROM quiz_pending')
            if pending:
                st.write(f"**{len(pending)} quizzes en attente**")
                
                for idx, pend in enumerate(pending):
                    st.markdown(f"**Q{idx+1}: {pend['question']}**")
                    st.markdown(f"A) {pend['option_a']} | B) {pend['option_b']} | C) {pend['option_c']} | D) {pend['option_d']}")
                    st.markdown(f"Correctes: {pend['reponses_correctes']}")
                    st.markdown(f"Explication: {pend['explication']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Approuver", key=f"app_{pend['id']}", use_container_width=True):
                            # Créer la série si elle n'existe pas
                            s = db.f1('SELECT id FROM series WHERE nom=?', (pend['categorie'],))
                            if not s:
                                db.q('INSERT INTO series (nom) VALUES (?)', (pend['categorie'],))
                                s = db.f1('SELECT id FROM series WHERE nom=?', (pend['categorie'],))
                            
                            # Ajouter le quiz
                            db.q('INSERT INTO quiz (series_id,question,option_a,option_b,option_c,option_d,reponses_correctes,explication) VALUES (?,?,?,?,?,?,?,?)',
                                (s['id'], pend['question'], pend['option_a'], pend['option_b'], pend['option_c'], pend['option_d'], pend['reponses_correctes'], pend['explication']))
                            
                            # Supprimer de pending
                            db.q('DELETE FROM quiz_pending WHERE id=?', (pend['id'],))
                            st.success("✅ Quiz approuvé!")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Rejeter", key=f"rej_{pend['id']}", use_container_width=True):
                            db.q('DELETE FROM quiz_pending WHERE id=?', (pend['id'],))
                            st.info("❌ Quiz rejeté")
                            st.rerun()
                    
                    st.divider()
            else:
                st.info("Aucun quiz en attente")
        
        elif st.session_state.admin_tab == "users":
            st.subheader("👥 Gestion des Apprenants")
            
            users = db.fa('SELECT * FROM utilisateurs WHERE role="apprenant"')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(users))
            with col2:
                active = len([u for u in users if u['status']=='actif'])
                st.metric("Actifs", active)
            with col3:
                blocked = len([u for u in users if u['status']=='bloqué'])
                st.metric("Bloqués", blocked)
            
            st.divider()
            
            for u in users:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    icon = "✅" if u['status']=='actif' else "🔒"
                    st.markdown(f"{icon} **{u['prenom']} {u['nom']}**")
                    st.caption(f"📧 {u['email']} | Session: {u['session_minutes']}min")
                
                with col2:
                    if st.button("Bloquer" if u['status']=='actif' else "Débloquer", key=f"block_{u['id']}", use_container_width=True):
                        new_status = 'bloqué' if u['status']=='actif' else 'actif'
                        db.q('UPDATE utilisateurs SET status=? WHERE id=?', (new_status, u['id']))
                        st.rerun()
                
                with col3:
                    new_dur = st.number_input("Min", 5, 1440, u['session_minutes'], key=f"dur_{u['id']}", step=1)
                    if new_dur != u['session_minutes']:
                        db.q('UPDATE utilisateurs SET session_minutes=? WHERE id=?', (new_dur, u['id']))
                        st.rerun()
                
                with col4:
                    if st.button("Supprimer", key=f"del_{u['id']}", use_container_width=True):
                        db.q('DELETE FROM utilisateurs WHERE id=?', (u['id'],))
                        st.rerun()
                
                st.divider()
        
        elif st.session_state.admin_tab == "feedback":
            st.subheader("💬 Feedback des Apprenants")
            
            feedbacks = db.fa('SELECT * FROM feedback ORDER BY id DESC')
            
            if feedbacks:
                for fb in feedbacks:
                    st.markdown(f"**{fb['titre']}** - Type: {fb['type']}")
                    st.markdown(f"📧 {fb['email']}")
                    st.markdown(f"Message: {fb['message']}")
                    st.divider()
            else:
                st.info("Aucun feedback")
