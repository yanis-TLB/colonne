import streamlit as st
import os
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
from datetime import date

load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Labo Q - Gestion Colonnes HPLC",
    page_icon="🧪",
    layout="wide"
)

# Connexion Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Gestion de l'authentification
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

st.title("🧪 Laboratoire Q - Gestion des Colonnes HPLC")

# Sidebar de connexion
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/chromatography.png", width=80)
    
    if not st.session_state.authenticated:
        st.subheader("🔐 Connexion")
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter"):
            if email == "admin@labo.com" and password == "Admin123!":
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.success("✅ Connecté !")
                st.rerun()
            else:
                st.error("❌ Email ou mot de passe incorrect")
    else:
        st.success(f"👋 Connecté : {st.session_state.user_email}")
        if st.button("🚪 Déconnexion"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.rerun()
        
        st.divider()
        st.caption("📊 Navigation")

# Contenu principal (uniquement connecté)
if st.session_state.authenticated:
    
    # Menu principal
    menu = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "📋 Gestion des Colonnes", "🔬 Enregistrer une Analyse", "📈 Historique", "🔍 Recherche"]
    )
    
    # PAGE 1: DASHBOARD
    if menu == "📊 Dashboard":
        st.header("📊 Tableau de bord")
        try:
            colonnes = supabase.table("colonnes").select("*").execute().data
            analyses = supabase.table("analyses").select("*").execute().data
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔬 Colonnes totales", len(colonnes))
            with col2:
                actives = len([c for c in colonnes if c.get('statut') == 'active'])
                st.metric("✅ Colonnes actives", actives)
            with col3:
                st.metric("📊 Analyses totales", len(analyses))
            with col4:
                usure = len([c for c in colonnes if c.get('injections_totales', 0) > c.get('injections_max', 500) * 0.8])
                st.metric("⚠️ Usure >80%", usure)
        except Exception as e:
            st.info("Ajoutez d'abord des colonnes")
    
    # PAGE 2: GESTION DES COLONNES
    elif menu == "📋 Gestion des Colonnes":
        st.header("📋 Gestion des Colonnes")
        
        with st.expander("➕ Ajouter une colonne", expanded=True):
            with st.form("add_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    code_colonne = st.text_input("Code Colonne*", placeholder="Ex: COL-001")
                    marque = st.text_input("Marque*")
                    code_usp = st.selectbox("Code USP*", ["L1 (C18)", "L7 (C8)", "L11 (Phényle)", "L14 (Silice)", "L20 (Diol)", "Autre"])
                    numero_serie = st.text_input("Numéro de série*")
                    longueur = st.number_input("Longueur (mm)", value=250)
                
                with col2:
                    diam_int = st.number_input("Diamètre interne (mm)", value=4.6, step=0.1)
                    diam_grains = st.number_input("Diamètre grains (µm)", value=3.5, step=0.1)
                    photo_url = st.text_input("URL de la photo (optionnel)")
                
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
                                "statut": "active"
                            }).execute()
                            st.success(f"✅ Colonne {code_colonne} ajoutée !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur: {e}")
                    else:
                        st.warning("Champs obligatoires manquants")
        
        # Liste des colonnes
        colonnes = supabase.table("colonnes").select("*").execute().data
        if colonnes:
            st.subheader("📊 Inventaire")
            df = pd.DataFrame(colonnes)
            st.dataframe(df[['code_colonne', 'marque', 'code_usp', 'numero_serie', 'longueur_mm', 'diametre_interne', 'statut']], use_container_width=True)
    
    # PAGE 3: ANALYSES
    elif menu == "🔬 Enregistrer une Analyse":
        st.header("🔬 Enregistrer une analyse")
        colonnes = supabase.table("colonnes").select("*").eq("statut", "active").execute().data
        if colonnes:
            with st.form("ana_form"):
                options = {f"{c['code_colonne']} - {c['marque']}": c['id'] for c in colonnes}
                selection = st.selectbox("Colonne", list(options.keys()))
                type_ana = st.selectbox("Type", ["Dissolution", "Uniformité de Teneur", "Dosage"])
                resultat = st.selectbox("Résultat", ["OK", "Hors spé"])
                chimiste = st.text_input("Chimiste")
                if st.form_submit_button("Enregistrer"):
                    st.success("Analyse enregistrée !")
                    st.balloons()
        else:
            st.warning("Ajoutez d'abord des colonnes")
    
    # PAGE 4: HISTORIQUE
    elif menu == "📈 Historique":
        st.header("📈 Historique")
        analyses = supabase.table("analyses").select("*").execute().data
        if analyses:
            st.dataframe(pd.DataFrame(analyses))
        else:
            st.info("Aucune analyse")
    
    # PAGE 5: RECHERCHE
    elif menu == "🔍 Recherche":
        st.header("🔍 Recherche")
        colonnes = supabase.table("colonnes").select("*").execute().data
        if colonnes:
            df = pd.DataFrame(colonnes)
            usp_filter = st.selectbox("Code USP", ["Tous"] + list(df['code_usp'].unique()))
            if usp_filter != "Tous":
                df = df[df['code_usp'] == usp_filter]
            st.dataframe(df[['code_colonne', 'marque', 'code_usp', 'longueur_mm', 'diametre_interne']], use_container_width=True)
        else:
            st.info("Aucune colonne")

else:
    st.info("👈 Connectez-vous pour accéder à l'application")
