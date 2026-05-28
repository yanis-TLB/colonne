import streamlit as st
import pandas as pd

def show_recherche(supabase):
    st.header("🔍 Recherche de colonnes HPLC")

    try:
     colonnes = supabase.table("colonnes").select("*")
        if not colonnes or isinstance(colonnes, dict):
            st.info("Aucune colonne dans la base de données.")
            return

        df = pd.DataFrame(colonnes)

        if 'types_analyse' in df.columns:
            df['types_analyse'] = df['types_analyse'].apply(
                lambda x: x if isinstance(x, list) else []
            )
        else:
            df['types_analyse'] = [[] for _ in range(len(df))]

        with st.expander("🎛️ Filtres de recherche", expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**🏷️ Identification**")
                marques_dispo = ["Toutes"] + sorted(df['marque'].dropna().unique().tolist())
                marque_filter = st.selectbox("Marque", marques_dispo)
                usp_dispo = ["Tous"] + sorted(df['code_usp'].dropna().unique().tolist())
                usp_filter = st.selectbox("Code USP / Type de phase", usp_dispo)
                statut_filter = st.selectbox("Statut", ["Tous", "active", "inactive"])

            with col2:
                st.markdown("**📐 Dimensions**")
                longueurs_dispo = sorted(df['longueur_mm'].dropna().unique().tolist())
                if longueurs_dispo:
                    lon_min, lon_max = int(min(longueurs_dispo)), int(max(longueurs_dispo))
                    if lon_min == lon_max:
                        lon_max = lon_min + 1
                    longueur_range = st.slider("Longueur (mm)", lon_min, lon_max, (lon_min, lon_max))
                else:
                    longueur_range = (0, 500)

                diam_int_dispo = sorted(df['diametre_interne'].dropna().unique().tolist())
                if diam_int_dispo:
                    di_min, di_max = float(min(diam_int_dispo)), float(max(diam_int_dispo))
                    if di_min == di_max:
                        di_max = di_min + 0.1
                    diam_int_range = st.slider("Diamètre interne (mm)", round(di_min,1), round(di_max,1), (round(di_min,1), round(di_max,1)), step=0.1)
                else:
                    diam_int_range = (1.0, 10.0)

                grains_dispo = sorted(df['diametre_grains'].dropna().unique().tolist())
                if grains_dispo:
                    gr_min, gr_max = float(min(grains_dispo)), float(max(grains_dispo))
                    if gr_min == gr_max:
                        gr_max = gr_min + 0.1
                    grains_range = st.slider("Diamètre grains (µm)", round(gr_min,1), round(gr_max,1), (round(gr_min,1), round(gr_max,1)), step=0.1)
                else:
                    grains_range = (0.5, 10.0)

            with col3:
                st.markdown("**🧪 Usage analytique**")
                tous_types = sorted({t for sous_liste in df['types_analyse'] for t in sous_liste})
                types_filter = st.multiselect("Types d'analyse", options=tous_types, placeholder="Sélectionner...")
                st.markdown("**🔎 Recherche libre**")
                search_text = st.text_input("Code colonne / N° série", placeholder="ex: COL-001")

        df_filtre = df.copy()

        if marque_filter != "Toutes":
            df_filtre = df_filtre[df_filtre['marque'] == marque_filter]
        if usp_filter != "Tous":
            df_filtre = df_filtre[df_filtre['code_usp'] == usp_filter]
        if statut_filter != "Tous":
            df_filtre = df_filtre[df_filtre['statut'] == statut_filter]

        df_filtre = df_filtre[
            (df_filtre['longueur_mm'] >= longueur_range[0]) &
            (df_filtre['longueur_mm'] <= longueur_range[1])
        ]
        df_filtre = df_filtre[
            (df_filtre['diametre_interne'] >= diam_int_range[0]) &
            (df_filtre['diametre_interne'] <= diam_int_range[1])
        ]
        df_filtre = df_filtre[
            (df_filtre['diametre_grains'] >= grains_range[0]) &
            (df_filtre['diametre_grains'] <= grains_range[1])
        ]

        if types_filter:
            df_filtre = df_filtre[
                df_filtre['types_analyse'].apply(lambda lst: any(t in lst for t in types_filter))
            ]

        if search_text:
            mask = (
                df_filtre['code_colonne'].str.contains(search_text, case=False, na=False) |
                df_filtre['numero_serie'].str.contains(search_text, case=False, na=False)
            )
            df_filtre = df_filtre[mask]

        nb = len(df_filtre)
        couleur = "🟢" if nb > 0 else "🔴"
        st.subheader(f"{couleur} {nb} colonne(s) trouvée(s)")

        if not df_filtre.empty:
            col_reset, col_export = st.columns([1, 1])
            with col_reset:
                if st.button("🔄 Réinitialiser les filtres"):
                    st.rerun()
            with col_export:
                csv = df_filtre.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Exporter CSV", data=csv,
                    file_name="colonnes_filtrees.csv", mime="text/csv")

            colonnes_affichees = [c for c in [
                'code_colonne', 'marque', 'code_usp', 'longueur_mm',
                'diametre_interne', 'diametre_grains', 'numero_serie',
                'statut', 'types_analyse', 'commentaire'
            ] if c in df_filtre.columns]

            df_affichage = df_filtre[colonnes_affichees].copy()
            df_affichage['types_analyse'] = df_affichage['types_analyse'].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else ""
            )

            st.dataframe(
                df_affichage.rename(columns={
                    'code_colonne': 'Code', 'marque': 'Marque',
                    'code_usp': 'Phase (USP)', 'longueur_mm': 'L (mm)',
                    'diametre_interne': 'DI (mm)', 'diametre_grains': 'dp (µm)',
                    'numero_serie': 'N° Série', 'statut': 'Statut',
                    'types_analyse': "Types d'analyse", 'commentaire': 'Commentaire'
                }),
                use_container_width=True, hide_index=True
            )

            st.markdown("---")
            st.subheader("🔬 Détail colonne")
            code_choisi = st.selectbox("Sélectionner une colonne", df_filtre['code_colonne'].tolist())

            if code_choisi:
                row = df_filtre[df_filtre['code_colonne'] == code_choisi].iloc[0]
                d1, d2, d3 = st.columns(3)
                with d1:
                    st.metric("Phase stationnaire", row.get('code_usp', 'N/A'))
                    st.metric("Marque", row.get('marque', 'N/A'))
                with d2:
                    st.metric("Longueur", f"{row.get('longueur_mm', 'N/A')} mm")
                    st.metric("Ø interne", f"{row.get('diametre_interne', 'N/A')} mm")
                with d3:
                    st.metric("Ø grains", f"{row.get('diametre_grains', 'N/A')} µm")
                    st.metric("Statut", row.get('statut', 'N/A'))

                if row.get('types_analyse'):
                    st.markdown("**Types d'analyse :**")
                    for t in row['types_analyse']:
                        st.markdown(f"- {t}")

                if row.get('photo_url'):
                    st.image(row['photo_url'], width=200, caption=f"Colonne {code_choisi}")

                if row.get('commentaire'):
                    st.info(f"💬 {row['commentaire']}")
        else:
            st.warning("Aucune colonne ne correspond aux critères sélectionnés.")

    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")