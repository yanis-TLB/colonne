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
            st.metric("🔬 Nombre total de colonnes", len(colonnes))
            
            if colonnes:
                df = pd.DataFrame(colonnes)
                actives = len(df[df['statut'] == 'active'])
                st.metric("✅ Colonnes actives", actives)
        except:
            st.info("Ajoutez des colonnes")
    
    elif menu == "📋 Gestion des Colonnes":
        st.header("📋 Gestion des Colonnes")
        
        with st.expander("➕ Ajouter une colonne", expanded=True):
            with st.form("add_form"):
                col1, col2 = st.columns(2)
                with col1:
                    code_colonne = st.text_input("Code Colonne*")
                    marque = st.text_input("Marque*")
                    code_usp = st.selectbox("Code USP*", ["L1 (C18)", "L7 (C8)", "L11 (Phényle)"])
                    numero_serie = st.text_input("Numéro de série*")
                with col2:
                    longueur = st.number_input("Longueur (mm)", value=250)
                    diam_int = st.number_input("Diamètre interne (mm)", value=4.6)
                    diam_grains = st.number_input("Diamètre grains (µm)", value=3.5)
                    commentaire = st.text_area("Commentaire")
                
                if st.form_submit_button("Enregistrer"):
                    if code_colonne and marque:
                        try:
                            supabase.table("colonnes").insert({
                                "code_colonne": code_colonne,
                                "marque": marque,
                                "code_usp": code_usp,
                                "numero_serie": numero_serie,
                                "longueur_mm": longueur,
                                "diametre_interne": diam_int,
                                "diametre_grains": diam_grains,
                                "commentaire": commentaire,
                                "statut": "active"
                            }).execute()
                            st.success("Colonne ajoutée !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur: {e}")
        
        data = supabase.table("colonnes").select("*").execute().data
        if data:
            st.dataframe(pd.DataFrame(data))
    
    elif menu == "🔍 Recherche":
        from pages.recherche import show_recherche
        show_recherche(supabase)

else:
    st.info("Connectez-vous")
