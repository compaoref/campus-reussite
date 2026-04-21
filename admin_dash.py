import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Campus Réussite", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.05);
}
.stat {
    font-size: 28px;
    font-weight: bold;
    color: #2E7D32;
}
</style>
""", unsafe_allow_html=True)

# --- LOAD CSV (optimisé cache) ---
@st.cache_data
def load_data():
    if os.path.exists("data_quizzes.csv"):
        try:
            return pd.read_csv("data_quizzes.csv", encoding="utf-8")
        except:
            return pd.read_csv("data_quizzes.csv", encoding="latin1")
    return pd.DataFrame()

df = load_data()

# --- SESSION STATE ---
if "answers" not in st.session_state:
    st.session_state.answers = {}

if "validated" not in st.session_state:
    st.session_state.validated = {}

if "score" not in st.session_state:
    st.session_state.score = 0

# --- SIDEBAR ---
menu = st.sidebar.radio("Navigation", [
    "🏠 Dashboard",
    "🧠 Quiz",
    "📊 Résultat"
])

# --- DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("📊 Tableau de bord")

    col1, col2 = st.columns(2)

    col1.markdown(f"""
    <div class="card">
        <div class="stat">{len(df)}</div>
        <div>Total questions</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="card">
        <div class="stat">{st.session_state.score}</div>
        <div>Score actuel</div>
    </div>
    """, unsafe_allow_html=True)

# --- QUIZ ---
elif menu == "🧠 Quiz":
    st.title("🧠 Test interactif")

    if df.empty:
        st.warning("Aucun quiz disponible")
    else:
        for i, row in df.iterrows():
            st.markdown(f"### Question {i+1}")
            st.write(row["question"])

            options = [row["a"], row["b"], row["c"], row["d"]]

            choix = st.radio(
                "Choisis ta réponse",
                options,
                key=f"q_{i}"
            )

            st.session_state.answers[i] = choix

            # Bouton valider individuel
            if st.button(f"Valider Q{i+1}", key=f"val_{i}"):

                if choix == row["reponse"]:
                    st.success("✅ Bonne réponse")
                    st.session_state.validated[i] = True
                else:
                    st.error(f"❌ Mauvaise réponse")
                    st.info(f"Réponse correcte : {row['reponse']}")
                    st.session_state.validated[i] = False

        st.write("---")

        # Score global
        if st.button("📊 Calculer le score"):
            score = sum(1 for v in st.session_state.validated.values() if v)
            st.session_state.score = score
            st.success(f"🎯 Score : {score}/{len(df)}")

# --- RESULTAT ---
elif menu == "📊 Résultat":
    st.title("📊 Résultat final")

    st.markdown(f"""
    <div class="card">
        <div class="stat">{st.session_state.score}</div>
        <div>Score obtenu</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Recommencer"):
        st.session_state.answers = {}
        st.session_state.validated = {}
        st.session_state.score = 0
        st.success("Réinitialisé")
