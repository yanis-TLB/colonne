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
    menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "📋 Gestion des Colonnes", "🔍 Recherche"])
    
    if menu == "📊 Dashboard":
        st.header("📊 Dashboard")
        try:
            colonnes = supabase.table("colonnes").select("*").execute().data
            analyses = supabase.table("analyses").select("*").execute().data
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔬 Colonnes", len(colonnes))
            with col2:
                st.metric("📊 Analyses", len(analyses))
            with col3:
                actives = len([c for c in colonnes if c.get('statut') == 'active'])
                st.metric("✅ Actives", actives)
        except:
            st.info("Ajoutez des données")
    
    elif menu == "📋 Gestion des Colonnes":
        st.header("📋 Gestion des Colonnes")
        
        with st.expander("➕ Ajouter une colonne", expanded=True):
            with st.form("add_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    code_colonne = st.text_input("Code Colonne*")
                    marque = st.text_input("Marque*")
                    code_usp = st.selectbox("Code USP*", ["L1 (C18)", "L7 (C8)", "L11 (Phényle)", "L14 (Silice)", "L20 (Diol)", "Autre"])
                    numero_serie = st.text_input("Numéro de série*")
                    longueur = st.number_input("Longueur (mm)", min_value=10, max_value=500, value=250)
                
                with col2:
                    diam_int = st.number_input("Diamètre interne (mm)", min_value=1.0, max_value=50.0, value=4.6, step=0.1)
                    diam_grains = st.number_input("Diamètre grains (µm)", min_value=0.5, max_value=10.0, value=3.5, step=0.1)
                    photo_url = st.text_input("URL de la photo (optionnel)", placeholder="https://exemple.com/photo.jpg")
                    commentaire = st.text_area("Commentaire (optionnel)", placeholder="Informations supplémentaires")
                    types_analyse = st.multiselect("Types d'analyse associés", 
                        ["Dosage", "Dos des Substance apparentés", "Uniformité de Teneur", "Identification", "Dissolution"])
                
                if photo_url:
                    st.image(photo_url, width=150, caption="Aperçu")
                
                if st.form_submit_button("💾 Enregistrer"):
                    if code_colonne and marque and numero_serie:
                        try:
                            supabase.table("colonnes").insert({
                                "code_colonne": code_colonne,
                                "marque": marque,
                                "code_usp": code_usp,
                                "numero_serie": numero_serie,
                                "longueur_mm": longueur,
                                "diametre_interne": diam_int,
                                "diametre_grains": diam_grains,
                                "photo_url": photo_url if photo_url else None,
                                "commentaire": commentaire if commentaire else None,
                                "types_analyse": types_analyse if types_analyse else None,
                                "statut": "active"
                            }).execute()
                            st.success(f"✅ Colonne {code_colonne} ajoutée !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur: {e}")
                    else:
                        st.warning("Les champs Code Colonne, Marque et N° série sont obligatoires")
        
        st.subheader("📊 Liste des colonnes")
        try:
            data = supabase.table("colonnes").select("*").execute().data
            if data:
                st.dataframe(pd.DataFrame(data), use_container_width=True)
            else:
                st.info("Aucune colonne")
        except Exception as e:
            st.error(f"Erreur: {e}")
    
    elif menu == "🔍 Recherche":
        from pages.recherche import show_recherche
        show_recherche(supabase)

else:
    st.info("👈 Connectez-vous pour accéder à l'application")