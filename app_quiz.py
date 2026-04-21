import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Campus Réussite - Apprendre", layout="centered")

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
    }
    .question-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #ddd;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.markdown("<h1 style='color: #2E7D32;'>🎓 Campus Réussite</h1>", unsafe_allow_html=True)

st.write("---")

# --- CHARGEMENT ---
if os.path.exists("data_quizzes.csv"):
    df_quiz = pd.read_csv("data_quizzes.csv")
    
    user_name = st.sidebar.text_input("Ton Prénom / Nom", value="Candidat")

    for i, row in df_quiz.iterrows():
        st.markdown(f"""
            <div class='question-card'>
                <h3 style='margin-top: 0;'>Question {i+1}</h3>
                <p>{row['question']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        options = [row['a'], row['b'], row['c'], row['d']]
        choix = st.radio("Sélectionnez votre réponse :", options, key=f"q_{i}")
        
        if st.button(f"Vérifier la réponse {i+1}", key=f"btn_{i}"):
            if choix == row['reponse']:
                st.success(f"🎯 Bravo {user_name} !")
                st.balloons()
            else:
                st.error(f"❌ La réponse était : {row['reponse']}")
        st.write("")
else:
    st.warning("👋 En attente des données de l'administrateur...")
