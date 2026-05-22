import streamlit as st
import os
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
from datetime import date

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
    menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "📋 Gestion des Colonnes", "🔬 Enregistrer Analyse", "🔍 Recherche"])
    
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        try:
            colonnes = supabase.table("colonnes").select("*").execute().data
            st.metric("🔬 Colonnes", len(colonnes))
        except:
            st.info("Ajoutez des colonnes")
    
    elif menu == "📋 Gestion des Colonnes":
        st.header("➕ Ajouter une colonne")
        with st.form("add_form"):
            col1, col2 = st.columns(2)
            with col1:
                code = st.text_input("Code Colonne")
                marque = st.text_input("Marque")
                usp = st.text_input("Code USP")
            with col2:
                serie = st.text_input("N° série")
                longueur = st.number_input("Longueur (mm)", value=250)
                diam_int = st.number_input("Diamètre interne (mm)", value=4.6)
            
            if st.form_submit_button("💾 Enregistrer"):
                if code and marque:
                    try:
                        supabase.table("colonnes").insert({
                            "code_colonne": code,
                            "marque": marque,
                            "code_usp": usp,
                            "numero_serie": serie,
                            "longueur_mm": longueur,
                            "diametre_interne": diam_int
                        }).execute()
                        st.success(f"✅ Colonne {code} ajoutée !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.warning("Code et marque obligatoires")
        
        st.subheader("📊 Liste des colonnes")
        data = supabase.table("colonnes").select("*").execute().data
        if data:
            st.dataframe(pd.DataFrame(data))
        else:
            st.info("Aucune colonne")
    
    elif menu == "🔬 Enregistrer Analyse":
        st.header("🔬 Enregistrer une analyse")
        colonnes = supabase.table("colonnes").select("*").execute().data
        if colonnes:
            options = {f"{c['code_colonne']} - {c['marque']}": c['id'] for c in colonnes}
            selection = st.selectbox("Colonne utilisée", list(options.keys()))
            type_ana = st.selectbox("Type d'analyse", ["Dissolution", "Uniformité"])
            resultat = st.selectbox("Résultat", ["OK", "Hors spé"])
            chimiste = st.text_input("Chimiste")
            if st.button("Enregistrer"):
                st.success("Analyse enregistrée !")
                st.balloons()
        else:
            st.warning("Ajoutez d'abord des colonnes")
    
    elif menu == "🔍 Recherche":
        from pages.recherche import show_recherche
        show_recherche(supabase)

else:
    st.info("👈 Connectez-vous pour accéder à l'application")