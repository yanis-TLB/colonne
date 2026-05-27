import streamlit as st
import os
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

st.set_page_config(page_title="Labo Q - Gestion Colonnes HPLC", page_icon="🧪", layout="wide")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

st.title("🧪 Laboratoire Q - Gestion des Colonnes HPLC")

with st.sidebar:
    if not st.session_state.authenticated:
        st.subheader("🔐 Connexion")
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if email == "admin@labo.com" and password == "Admin123!":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Identifiants incorrects")
    else:
        st.success("👋 Connecté")
        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()

if st.session_state.authenticated:
    menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "📋 Gestion des Colonnes", "🔍 Recherche"])
    
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        try:
            colonnes = supabase.table("colonnes").select("*").execute().data
            st.metric("🔬 Colonnes", len(colonnes))
        except:
            st.info("Ajoutez des colonnes")
    
    elif menu == "📋 Gestion des Colonnes":
        st.header("📋 Gestion des Colonnes")
        
        with st.expander("➕ Ajouter une colonne"):
            with st.form("add_form"):
                code = st.text_input("Code Colonne")
                marque = st.text_input("Marque")
                usp = st.text_input("Code USP")
                serie = st.text_input("N° série")
                if st.form_submit_button("Enregistrer"):
                    if code and marque:
                        try:
                            supabase.table("colonnes").insert({
                                "code_colonne": code,
                                "marque": marque,
                                "code_usp": usp,
                                "numero_serie": serie
                            }).execute()
                            st.success("Colonne ajoutée !")
                        except Exception as e:
                            st.error(f"Erreur: {e}")
        
        data = supabase.table("colonnes").select("*").execute().data
        if data:
            st.dataframe(pd.DataFrame(data))
    
    elif menu == "🔍 Recherche":
        st.header("🔍 Recherche")
        data = supabase.table("colonnes").select("*").execute().data
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df)

else:
    st.info("Connectez-vous")
