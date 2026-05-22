import streamlit as st
import pandas as pd

def show_recherche(supabase):
    st.header("🔍 ColStore - Recherche de colonnes")
    
    # Récupérer toutes les colonnes
    colonnes = supabase.table("colonnes").select("*").execute().data
    
    if not colonnes:
        st.info("Aucune colonne dans la base de données")
        return
    
    df = pd.DataFrame(colonnes)
    
    # ========== FILTRES ==========
    st.subheader("📋 Filtres de recherche")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtre Code USP
        usp_options = ["Tous"] + sorted(df['code_usp'].unique().tolist())
        code_usp = st.selectbox("Code USP", usp_options)
    
    with col2:
        # Filtre Longueur
        longueurs = sorted(df['longueur_mm'].unique().tolist())
        longueur = st.selectbox("Longueur (mm)", ["Tous"] + longueurs)
    
    with col3:
        # Filtre Diamètre interne
        diametres = sorted(df['diametre_interne'].unique().tolist())
        diametre = st.selectbox("Diamètre interne (mm)", ["Tous"] + diametres)
    
    # ========== APPLICATION DES FILTRES ==========
    df_filtre = df.copy()
    
    if code_usp != "Tous":
        df_filtre = df_filtre[df_filtre['code_usp'] == code_usp]
    if longueur != "Tous":
        df_filtre = df_filtre[df_filtre['longueur_mm'] == longueur]
    if diametre != "Tous":
        df_filtre = df_filtre[df_filtre['diametre_interne'] == diametre]
    
    # ========== RÉSULTATS ==========
    st.subheader(f"📊 Résultats ({len(df_filtre)} colonne(s))")
    
    if not df_filtre.empty:
        # Tableau des résultats
        colonnes_affichage = ['code_colonne', 'marque', 'code_usp', 'longueur_mm', 
                              'diametre_interne', 'diametre_grains', 'numero_serie', 'statut']
        
        st.dataframe(
            df_filtre[colonnes_affichage].rename(columns={
                'code_colonne': 'Code Colonne',
                'marque': 'Marque',
                'code_usp': 'Code USP',
                'longueur_mm': 'Longueur (mm)',
                'diametre_interne': 'Diamètre (mm)',
                'diametre_grains': 'Grains (µm)',
                'numero_serie': 'N° Série',
                'statut': 'Statut'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Bouton export
        if st.button("📥 Exporter les résultats"):
            csv = df_filtre[colonnes_affichage].to_csv(index=False)
            st.download_button("Télécharger CSV", csv, "colonnes_filtrees.csv", "text/csv")
    else:
        st.warning("Aucune colonne ne correspond aux critères")