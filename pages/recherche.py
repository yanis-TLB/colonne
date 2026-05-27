import streamlit as st
import pandas as pd

def show_recherche(supabase):
    st.header("🔍 Recherche de colonnes")
    
    try:
        colonnes = supabase.table("colonnes").select("*").execute().data
        
        if not colonnes:
            st.info("Aucune colonne dans la base de données")
            return
        
        df = pd.DataFrame(colonnes)
        
        st.subheader("📋 Filtres")
        
        col1, col2 = st.columns(2)
        with col1:
            usp_filter = st.selectbox("Code USP", ["Tous"] + sorted(df['code_usp'].unique().tolist()))
        with col2:
            marque_filter = st.selectbox("Marque", ["Tous"] + sorted(df['marque'].unique().tolist()))
        
        df_filtre = df.copy()
        if usp_filter != "Tous":
            df_filtre = df_filtre[df_filtre['code_usp'] == usp_filter]
        if marque_filter != "Tous":
            df_filtre = df_filtre[df_filtre['marque'] == marque_filter]
        
        st.subheader(f"📊 Résultats ({len(df_filtre)} colonnes)")
        
        if not df_filtre.empty:
            st.dataframe(df_filtre[['code_colonne', 'marque', 'code_usp', 'longueur_mm', 'diametre_interne', 'statut']], use_container_width=True)
        else:
            st.warning("Aucun résultat")
            
    except Exception as e:
        st.error(f"Erreur: {e}")