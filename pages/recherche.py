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
    
    # ========== SECTION FILTRES ==========
    st.subheader("📋 Filtres de recherche")
    st.markdown("---")
    
    # Ligne 1 : Filtres principaux
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtre Code USP
        usp_options = ["Tous"] + sorted(df['code_usp'].unique().tolist())
        code_usp = st.selectbox("🔬 Code USP", usp_options)
    
    with col2:
        # Filtre Marque
        marques = ["Tous"] + sorted(df['marque'].unique().tolist())
        marque = st.selectbox("🏷️ Marque", marques)
    
    with col3:
        # Filtre Statut
        statuts = ["Tous", "active", "usée", "HS"]
        statut = st.selectbox("📊 Statut", statuts)
    
    # Ligne 2 : Filtres dimensions
    st.markdown("---")
    col4, col5, col6 = st.columns(3)
    
    with col4:
        # Filtre Longueur (slider)
        min_long = int(df['longueur_mm'].min())
        max_long = int(df['longueur_mm'].max())
        longueur = st.slider("📏 Longueur (mm)", min_long, max_long, (min_long, max_long))
    
    with col5:
        # Filtre Diamètre interne (slider)
        min_diam = float(df['diametre_interne'].min())
        max_diam = float(df['diametre_interne'].max())
        diametre = st.slider("🎯 Diamètre interne (mm)", min_diam, max_diam, (min_diam, max_diam))
    
    with col6:
        # Filtre Diamètre grains (slider)
        min_grain = float(df['diametre_grains'].min())
        max_grain = float(df['diametre_grains'].max())
        grains = st.slider("⚫ Diamètre grains (µm)", min_grain, max_grain, (min_grain, max_grain))
    
    # Ligne 3 : Filtres texte
    st.markdown("---")
    col7, col8 = st.columns(2)
    
    with col7:
        # Recherche par code colonne
        code_recherche = st.text_input("🔎 Code Colonne", placeholder="Ex: COL-001")
    
    with col8:
        # Recherche par numéro de série
        serie_recherche = st.text_input("📝 Numéro de série", placeholder="Ex: WAT12345")
    
    # Ligne 4 : Filtre type d'analyse
    col9, col10 = st.columns(2)
    
    with col9:
        types_analyse_list = ["Tous", "Dosage", "Dos des Substance apparentés", "Uniformité de Teneur", "Identification", "Dissolution"]
        type_analyse_filtre = st.selectbox("🧪 Type d'analyse compatible", types_analyse_list)
    
    with col10:
        # Trier par
        tri_options = ["code_colonne", "marque", "code_usp", "longueur_mm", "diametre_interne"]
        tri = st.selectbox("📊 Trier par", tri_options)
    
    # ========== APPLICATION DES FILTRES ==========
    df_filtre = df.copy()
    
    # Filtre Code USP
    if code_usp != "Tous":
        df_filtre = df_filtre[df_filtre['code_usp'] == code_usp]
    
    # Filtre Marque
    if marque != "Tous":
        df_filtre = df_filtre[df_filtre['marque'] == marque]
    
    # Filtre Statut
    if statut != "Tous":
        df_filtre = df_filtre[df_filtre['statut'] == statut]
    
    # Filtre Longueur
    df_filtre = df_filtre[(df_filtre['longueur_mm'] >= longueur[0]) & (df_filtre['longueur_mm'] <= longueur[1])]
    
    # Filtre Diamètre
    df_filtre = df_filtre[(df_filtre['diametre_interne'] >= diametre[0]) & (df_filtre['diametre_interne'] <= diametre[1])]
    
    # Filtre Grains
    df_filtre = df_filtre[(df_filtre['diametre_grains'] >= grains[0]) & (df_filtre['diametre_grains'] <= grains[1])]
    
    # Filtre Code Colonne
    if code_recherche:
        df_filtre = df_filtre[df_filtre['code_colonne'].str.contains(code_recherche, case=False, na=False)]
    
    # Filtre Numéro de série
    if serie_recherche:
        df_filtre = df_filtre[df_filtre['numero_serie'].str.contains(serie_recherche, case=False, na=False)]
    
    # Filtre Type d'analyse (si la colonne existe)
    if type_analyse_filtre != "Tous" and 'types_analyse' in df_filtre.columns:
        df_filtre = df_filtre[df_filtre['types_analyse'].apply(lambda x: type_analyse_filtre in x if x else False)]
    
    # Tri
    df_filtre = df_filtre.sort_values(by=tri)
    
    # ========== RÉSULTATS ==========
    st.markdown("---")
    st.subheader(f"📊 Résultats de la recherche : {len(df_filtre)} colonne(s)")
    
    if not df_filtre.empty:
        # Affichage des résultats sous forme de cartes
        for _, row in df_filtre.iterrows():
            with st.container():
                col_img, col_info = st.columns([1, 4])
                
                with col_img:
                    if row.get('photo_url') and pd.notna(row.get('photo_url')):
                        st.image(row['photo_url'], width=120)
                    else:
                        st.image("https://img.icons8.com/color/96/000000/chromatography.png", width=120)
                
                with col_info:
                    st.markdown(f"""
                    ### 🧪 **{row['code_colonne']}** - {row['marque']}
                    | Propriété | Valeur |
                    |-----------|--------|
                    | **Code USP** | `{row['code_usp']}` |
                    | **N° Série** | `{row['numero_serie']}` |
                    | **Dimensions** | {row['longueur_mm']} mm × {row['diametre_interne']} mm × {row['diametre_grains']} µm |
                    | **Statut** | {row.get('statut', 'active')} |
                    | **Types d'analyse** | {row.get('types_analyse', 'Non spécifiés')} |
                    """)
                    
                    if row.get('commentaire'):
                        st.info(f"📝 {row['commentaire']}")
                
                st.markdown("---")
        
        # Bouton export
        col_export, col_empty = st.columns([1, 4])
        with col_export:
            if st.button("📥 Exporter les résultats en CSV"):
                cols_export = ['code_colonne', 'marque', 'code_usp', 'numero_serie', 'longueur_mm', 
                              'diametre_interne', 'diametre_grains', 'statut', 'types_analyse']
                csv = df_filtre[cols_export].to_csv(index=False)
                st.download_button("Télécharger CSV", csv, "recherche_colonnes.csv", "text/csv")
    else:
        st.warning("😕 Aucune colonne ne correspond aux critères de recherche")
        st.info("💡 Essayez de modifier vos filtres pour élargir la recherche")
    
    # ========== STATISTIQUES RAPIDES ==========
    with st.expander("📈 Statistiques des colonnes"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏷️ Marques différentes", df['marque'].nunique())
        with col2:
            st.metric("🔬 Codes USP différents", df['code_usp'].nunique())
        with col3:
            st.metric("✅ Colonnes actives", len(df[df['statut'] == 'active']))