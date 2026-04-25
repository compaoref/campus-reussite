import os
import sys
import traceback
import streamlit as st

# Global wrapper to surface any exception in the UI
try:
    import pandas as pd
    from database import db

    st.set_page_config(page_title="Campus Admin", layout="wide")

    # Quick DB diagnostic in top area (helps detect early DB/init issues)
    try:
        st.sidebar.markdown("### Debug DB (admin_dash)")
        st.sidebar.write("DB path:", db.get_db_path())
        dp = db.get_db_path()
        st.sidebar.write("exists:", os.path.exists(dp))
        if os.path.exists(dp):
            st.sidebar.write("size (bytes):", os.path.getsize(dp))
            try:
                import sqlite3
                conn = sqlite3.connect(dp)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [r[0] for r in cur.fetchall()]
                st.sidebar.write("tables:", tables)
                for t in tables:
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM {t}")
                        cnt = cur.fetchone()[0]
                        st.sidebar.write(f"{t}: {cnt}")
                    except Exception as e:
                        st.sidebar.write(f"count error {t}: {e}")
                conn.close()
            except Exception as e:
                st.sidebar.write("sqlite error:", e)
        st.sidebar.markdown("---")
    except Exception:
        # don't block the UI for DB diagnostic errors
        st.sidebar.write("DB diagnostic error")
        st.sidebar.write(traceback.format_exc())

    st.markdown("""
    <style>
        .header { background: linear-gradient(90deg, #1e293b, #0f172a); color: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; }
        .card { background: white; padding: 1.2rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem; }
        .stat { background: linear-gradient(90deg, #667eea, #764ba2); color: white; padding: 1rem; border-radius: 8px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

    # --- AUTH ---
    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("## 🔐 Administration")
            email = st.text_input("Email")
            pwd = st.text_input("Mot de passe", type="password")

            if st.button("Se Connecter", use_container_width=True, type="primary"):
                try:
                    admins = st.secrets.get("admins", {})
                    if email in admins and admins[email] == pwd:
                        st.session_state.admin_auth = True
                        st.session_state.admin_email = email
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects")
                except Exception:
                    st.error("⚠️ Erreur lors de la vérification des secrets")
    else:
        # --- DASHBOARD ---
        st.markdown(f"""
        <div class="header">
            <h2 style="margin:0">🎓 Campus Réussite - Admin</h2>
            <p style="margin:0.5rem 0 0; opacity:0.9">👤 {st.session_state.admin_email}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Déconnexion", key="logout"):
            st.session_state.admin_auth = False
            st.rerun()

        st.divider()

        # Temporary: Seed DB button for debugging (remove in production)
        with st.expander("⚠️ Outils de debug (temporaire)"):
            st.markdown("Bouton pour insérer des données de test dans la base (utilisez uniquement en dev).")
            if st.button("Seed DB (test)"):
                try:
                    db.add_user("Admin", "Campus", "admin@campus.test", "admin_campus", "adminpass")
                    db.add_user("Jean", "Dupont", "jean.dupont@test.com", "jdupont", "password123")
                    db.add_quiz("Quelle est la capitale de la France ?", "Londres", "Paris", "Rome", "Berlin", "Paris", "La capitale est Paris.", "Géographie")
                    db.add_quiz("2 + 2 = ?", "3", "4", "2", "22", "4", "Addition basique", "Maths")
                    db.add_pending_quiz("Pending question ?", "A", "B", "C", "D", "A", "Explication pending", "Divers", "seed.csv")
                    db.add_feedback("jean.dupont@test.com", "Super", "Très bon contenu", "Suggestion")
                    st.success("✅ Données de test insérées")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors du seed: {e}")
                    st.write(traceback.format_exc())

        st.divider()

        # --- TABS ---
        if "admin_tab" not in st.session_state:
            st.session_state.admin_tab = "dashboard"

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.admin_tab = "dashboard"
                st.rerun()
        with col2:
            if st.button("📤 Importer", use_container_width=True):
                st.session_state.admin_tab = "import"
                st.rerun()
        with col3:
            if st.button("👥 Apprenants", use_container_width=True):
                st.session_state.admin_tab = "users"
                st.rerun()
        with col4:
            if st.button("💬 Feedback", use_container_width=True):
                st.session_state.admin_tab = "feedback"
                st.rerun()

        st.divider()

        # === DASHBOARD ===
        if st.session_state.admin_tab == "dashboard":
            st.markdown("### 📊 Statistiques")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="stat"><div style="font-size:2rem; font-weight:bold">{len(db.get_all_users())}</div><div>Apprenants</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat"><div style="font-size:2rem; font-weight:bold">{db.get_quiz_count()}</div><div>Quiz Publiés</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="stat"><div style="font-size:2rem; font-weight:bold">{len(db.get_pending_quiz())}</div><div>En Révision</div></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="stat"><div style="font-size:2rem; font-weight:bold">{len(db.get_all_feedback())}</div><div>Feedbacks</div></div>', unsafe_allow_html=True)

            st.divider()
            st.markdown("### 📋 Quiz Publiés")

            quiz_list = db.get_all_quiz()
            st.write(f"**Total: {len(quiz_list)} quiz**")

            if quiz_list:
                df = pd.DataFrame(quiz_list)
                df = df[['question', 'reponses_correctes', 'categorie']]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun quiz")

        # === IMPORT ===
        elif st.session_state.admin_tab == "import":
            st.markdown("### 📤 Importer des Quiz")

            uploaded_file = st.file_uploader("Fichier CSV", type=["csv"])

            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
                    st.success(f"✅ {len(df)} lignes chargées")
                    st.dataframe(df, use_container_width=True, height=300)

                    if st.button("📥 Ajouter à la Révision", use_container_width=True, type="primary"):
                        count = 0
                        for _, row in df.iterrows():
                            if db.add_pending_quiz(
                                row['question'],
                                row['a'],
                                row['b'],
                                row['c'],
                                row['d'],
                                row['reponses_correctes'],
                                row['explication'],
                                row['categorie'],
                                uploaded_file.name
                            ):
                                count += 1
                        st.success(f"✅ {count} quiz ajoutés à la révision")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
                    st.write(traceback.format_exc())

            st.divider()
            st.markdown("### ⏳ Quiz en Révision")

            pending = db.get_pending_quiz()
            st.write(f"**{len(pending)} quiz en attente**")

            if pending:
                for idx, q in enumerate(pending):
                    with st.container():
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            st.markdown(f"**Q{q['id']}: {q['question']}**")
                            st.markdown(f"Catégorie: {q['categorie']}")

                            with st.expander("Détails"):
                                st.text(f"A) {q['option_a']}")
                                st.text(f"B) {q['option_b']}")
                                st.text(f"C) {q['option_c']}")
                                st.text(f"D) {q['option_d']}")
                                st.text(f"Réponses: {q['reponses_correctes']}")
                                st.text(f"Explication: {q['explication']}")

                            with st.expander("✏️ Modifier"):
                                question = st.text_input("Question", value=q['question'], key=f"q_{idx}_{q['id']}")
                                opt_a = st.text_input("A", value=q['option_a'], key=f"opt_a_{idx}_{q['id']}")
                                opt_b = st.text_input("B", value=q['option_b'], key=f"opt_b_{idx}_{q['id']}")
                                opt_c = st.text_input("C", value=q['option_c'], key=f"opt_c_{idx}_{q['id']}")
                                opt_d = st.text_input("D", value=q['option_d'], key=f"opt_d_{idx}_{q['id']}")
                                correct = st.text_input("Réponses", value=q['reponses_correctes'], key=f"r_{idx}_{q['id']}")
                                expl = st.text_area("Explication", value=q['explication'], key=f"e_{idx}_{q['id']}")
                                cat = st.text_input("Catégorie", value=q['categorie'], key=f"cat_{idx}_{q['id']}")

                                if st.button("Sauvegarder", key=f"save_{idx}_{q['id']}"):
                                    try:
                                        db.update_pending_quiz(q['id'], question, opt_a, opt_b, opt_c, opt_d, correct, expl, cat)
                                        st.success("✅ Modifié")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erreur sauvegarde: {e}")
                                        st.write(traceback.format_exc())

                        with col2:
                            col_a, col_r = st.columns(2)
                            with col_a:
                                if st.button("✅", key=f"accept_{idx}_{q['id']}", help="Accepter"):
                                    try:
                                        db.approve_pending_quiz(q['id'])
                                        st.success("✅ Accepté")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erreur accept: {e}")
                                        st.write(traceback.format_exc())
                            with col_r:
                                if st.button("❌", key=f"reject_{idx}_{q['id']}", help="Rejeter"):
                                    try:
                                        db.reject_pending_quiz(q['id'])
                                        st.info("❌ Rejeté")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erreur reject: {e}")
                                        st.write(traceback.format_exc())

except Exception as e:
    # If anything goes wrong during import/exec, show full traceback in UI and stderr
    try:
        st.error("L'application a rencontré une erreur. Voir détails ci-dessous.")
        st.text(traceback.format_exc())
    except Exception:
        # If even st isn't available, print to stderr
        print("Fatal error while rendering admin_dash:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
    # Always print to stderr for logs
    print("Unhandled exception in admin_dash.py:", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
