import streamlit as st
import pandas as pd

def show_recherche(supabase):
    st.header("🔍 Recherche de colonnes HPLC")

    try:
        colonnes = supabase.table("colonnes").select("*")

        if not colonnes or not isinstance(colonnes, list):
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
                marques = ["Toutes"] + sorted(df['marque'].dropna().unique().tolist())
                marque_filter = st.selectbox("Marque", marques)
                usps = ["Tous"] + sorted(df['code_usp'].dropna().unique().tolist())
                usp_filter = st.selectbox("Code USP", usps)
                statut_filter = st.selectbox("Statut", ["Tous", "active", "inactive"])

            with col2:
                st.markdown("**📐 Dimensions**")
                lons = sorted(df['longueur_mm'].dropna().unique().tolist())
                if lons:
                    lmin, lmax = int(min(lons)), int(max(lons))
                    if lmin == lmax:
                        lmax += 1
                    lon_range = st.slider("Longueur (mm)", lmin, lmax, (lmin, lmax))
                else:
                    lon_range = (0, 500)

                dis = sorted(df['diametre_interne'].dropna().unique().tolist())
                if dis:
                    dmin, dmax = round(float(min(dis)), 1), round(float(max(dis)), 1)
                    if dmin == dmax:
                        dmax += 0.1
                    di_range = st.slider("Diamètre interne (mm)", dmin, dmax, (dmin, dmax), step=0.1)
                else:
                    di_range = (1.0, 10.0)

                grs = sorted(df['diametre_grains'].dropna().unique().tolist())
                if grs:
                    gmin, gmax = round(float(min(grs)), 1), round(float(max(grs)), 1)
                    if gmin == gmax:
                        gmax += 0.1
                    gr_range = st.slider("Diamètre grains (µm)", gmin, gmax, (gmin, gmax), step=0.1)
                else:
                    gr_range = (0.5, 10.0)

            with col3:
                st.markdown("**🧪 Usage analytique**")
                tous_types = sorted({t for lst in df['types_analyse'] for t in lst})
                types_filter = st.multiselect("Types d'analyse", options=tous_types, placeholder="Sélectionner...")
                st.markdown("**🔎 Recherche libre**")
                search_text = st.text_input("Code colonne / N° série", placeholder="ex: COL-001")

        df_f = df.copy()
        if marque_filter != "Toutes":
            df_f = df_f[df_f['marque'] == marque_filter]
        if usp_filter != "Tous":
            df_f = df_f[df_f['code_usp'] == usp_filter]
        if statut_filter != "Tous":
            df_f = df_f[df_f['statut'] == statut_filter]
        df_f = df_f[(df_f['longueur_mm'] >= lon_range[0]) & (df_f['longueur_mm'] <= lon_range[1])]
        df_f = df_f[(df_f['diametre_interne'] >= di_range[0]) & (df_f['diametre_interne'] <= di_range[1])]
        df_f = df_f[(df_f['diametre_grains'] >= gr_range[0]) & (df_f['diametre_grains'] <= gr_range[1])]
        if types_filter:
            df_f = df_f[df_f['types_analyse'].apply(lambda l: any(t in l for t in types_filter))]
        if search_text:
            df_f = df_f[
                df_f['code_colonne'].str.contains(search_text, case=False, na=False) |
                df_f['numero_serie'].str.contains(search_text, case=False, na=False)
            ]

        nb = len(df_f)
        st.subheader(f"{'🟢' if nb > 0 else '🔴'} {nb} colonne(s) trouvée(s)")

        if not df_f.empty:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔄 Réinitialiser"):
                    st.rerun()
            with c2:
                st.download_button("📥 Exporter CSV",
                    data=df_f.to_csv(index=False).encode("utf-8"),
                    file_name="colonnes.csv", mime="text/csv")

            cols_show = [c for c in ['code_colonne','marque','code_usp','longueur_mm',
                'diametre_interne','diametre_grains','numero_serie','statut',
                'types_analyse','commentaire'] if c in df_f.columns]

            df_aff = df_f[cols_show].copy()
            df_aff['types_analyse'] = df_aff['types_analyse'].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else "")

            st.dataframe(df_aff.rename(columns={
                'code_colonne':'Code','marque':'Marque','code_usp':'Phase (USP)',
                'longueur_mm':'L (mm)','diametre_interne':'DI (mm)',
                'diametre_grains':'dp (µm)','numero_serie':'N° Série',
                'statut':'Statut','types_analyse':"Types d'analyse",'commentaire':'Commentaire'
            }), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("🔬 Détail colonne")
            code_choisi = st.selectbox("Sélectionner", df_f['code_colonne'].tolist())
            if code_choisi:
                row = df_f[df_f['code_colonne'] == code_choisi].iloc[0]
                d1, d2, d3 = st.columns(3)
                with d1:
                    st.metric("Phase", row.get('code_usp', 'N/A'))
                    st.metric("Marque", row.get('marque', 'N/A'))
                with d2:
                    st.metric("Longueur", f"{row.get('longueur_mm','N/A')} mm")
                    st.metric("Ø interne", f"{row.get('diametre_interne','N/A')} mm")
                with d3:
                    st.metric("Ø grains", f"{row.get('diametre_grains','N/A')} µm")
                    st.metric("Statut", row.get('statut', 'N/A'))
                if row.get('types_analyse'):
                    st.markdown("**Types d'analyse :**")
                    for t in row['types_analyse']:
                        st.markdown(f"- {t}")
                if row.get('photo_url'):
                    st.image(row['photo_url'], width=200)
                if row.get('commentaire'):
                    st.info(f"💬 {row['commentaire']}")
        else:
            st.warning("Aucune colonne ne correspond aux critères.")

    except Exception as e:
        st.error(f"Erreur : {e}")