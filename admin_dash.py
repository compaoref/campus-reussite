import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Admin - Campus Réussite", layout="wide")

# --- SÉCURITÉ ADMIN ---
def check_password():
    if "authenticated" not in st.session_state:
        st.title("🔐 Administration - Campus Réussite")
        user_input = st.text_input("Nom d'administrateur")
        pw_input = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter"):
            try:
                admins = st.secrets["admin_accounts"]
                if user_input in admins and pw_input == admins[user_input]:
                    st.session_state.authenticated = True
                    st.session_state.admin_name = user_input
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects.")
            except:
                # Mode secours si secrets non configurés
                if user_input == "admin" and pw_input == "1234":
                    st.session_state.authenticated = True
                    st.rerun()
        return False
    return True

if check_password():
    st.sidebar.title(f"Salut, {st.session_state.get('admin_name', 'Major')} !")
    menu = st.sidebar.radio("Navigation", ["📊 Statistiques", "📤 Importer des Quiz"])

    if menu == "📊 Statistiques":
        st.title("🚀 Tableau de bord Campus Réussite")
        if os.path.exists("data_quizzes.csv"):
            try:
                # Correction Unicode : on essaie UTF-8, puis Latin-1 si ça échoue
                try:
                    df_stats = pd.read_csv("data_quizzes.csv", encoding="utf-8")
                except UnicodeDecodeError:
                    df_stats = pd.read_csv("data_quizzes.csv", encoding="latin1")
                
                st.metric("Questions en ligne", len(df_stats))
                st.write("### Aperçu des données")
                st.dataframe(df_stats)
            except Exception as e:
                st.error(f"Erreur de lecture : {e}")
        else:
            st.warning("Aucun fichier de données trouvé. Veuillez importer un CSV.")

    elif menu == "📤 Importer des Quiz":
        st.title("📥 Mise à jour des Quiz")
        uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            if st.button("🚀 Publier sur la plateforme"):
                df.to_csv("data_quizzes.csv", index=False, encoding="utf-8")
                st.success("Base de données mise à jour ! Rebootez l'app apprenant si besoin.")
