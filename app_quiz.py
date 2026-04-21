import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Apprenant - Campus Réussite", layout="centered")

# --- LOGO & STYLE ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.markdown("<h1 style='color: #2E7D32;'>🎓 Campus Réussite</h1>", unsafe_allow_html=True)

st.write("---")

# --- CHARGEMENT ---
if os.path.exists("data_quizzes.csv"):
    try:
        # Même correction pour les accents ici
        try:
            df_quiz = pd.read_csv("data_quizzes.csv", encoding="utf-8")
        except UnicodeDecodeError:
            df_quiz = pd.read_csv("data_quizzes.csv", encoding="latin1")
        
        user_name = st.sidebar.text_input("Ton Nom", value="Candidat")
        
        for i, row in df_quiz.iterrows():
            st.subheader(f"Question {i+1}")
            st.write(row['question'])
            
            options = [row['a'], row['b'], row['c'], row['d']]
            choix = st.radio(f"Réponse pour Q{i+1}:", options, key=f"q_{i}")
            
            if st.button(f"Valider Q{i+1}", key=f"btn_{i}"):
                if choix == row['reponse']:
                    st.success(f"🎯 Bravo {user_name} !")
                    st.balloons()
                else:
                    st.error(f"❌ La réponse était : {row['reponse']}")
                    st.info(f"💡 {row['explication']}")
            st.write("---")
    except Exception as e:
        st.error(f"Erreur technique : {e}")
else:
    st.info("👋 Bonjour ! Les quiz arrivent bientôt. L'admin prépare les fichiers.")
