import streamlit as st
import pandas as pd
import plotly.express as px

# Fonction pour analyser les flux en tenant compte d'une recherche partielle d'adresse
def analyze_flows(df, wallet):
    wallet = wallet.lower()
    tokens = df["Token"].unique()
    results = []
    
    # Préparer recherche partielle : début 6 premiers + fin 4 derniers caractères
    wallet_start = wallet[:6]
    wallet_end = wallet[-4:]
    
    for token in tokens:
        df_token = df[df["Token"] == token]

        # Mask pour présence partielle dans 'From' et 'To'
        sent_mask = df_token["From"].str.lower().str.contains(wallet_start) & df_token["From"].str.lower().str.contains(wallet_end)
        received_mask = df_token["To"].str.lower().str.contains(wallet_start) & df_token["To"].str.lower().str.contains(wallet_end)

        total_sent = df_token[sent_mask]["USD"].sum()
        total_received = df_token[received_mask]["USD"].sum()
        net = total_received - total_sent
        results.append({
            "Token": token,
            "Total envoyé (USD)": round(total_sent, 4),
            "Total reçu (USD)": round(total_received, 4),
            "Net (USD)": round(net, 4),
            "Frais implicites (USD)": round(-net if net < 0 else 0, 4)
        })
    return pd.DataFrame(results)

# Titre
st.title("Analyse des transferts de tokens")

# Upload fichier CSV
uploaded_file = st.file_uploader("Importer fichier CSV des transferts")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Saisie adresse wallet
    wallet = st.text_input("Entrez l'adresse de votre wallet (ex : 0xabc123...)", "")

    if wallet:
        if st.button("Lancer l'analyse"):
            # Analyse
            summary_df = analyze_flows(df, wallet)

            # Afficher les détails des transferts
            st.subheader("📋 Détails des transferts détectés")
            st.dataframe(df)

            # Affichage résumé par token
            st.subheader(f"💰 Résumé des flux pour l'adresse : {wallet}")
            st.dataframe(summary_df)

            # Totaux
            total_sent = summary_df["Total envoyé (USD)"].sum()
            total_received = summary_df["Total reçu (USD)"].sum()
            total_fees = summary_df["Frais implicites (USD)"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total envoyé", f"${total_sent:.4f}")
            col2.metric("Total reçu", f"${total_received:.4f}")
            col3.metric("Frais implicites estimés", f"${total_fees:.4f}")

            # Graphique frais implicites par token
            st.subheader("📊 Répartition des frais implicites par token")
            if total_fees > 0:
                fig = px.bar(summary_df, x="Token", y="Frais implicites (USD)", title="Frais implicites par token")
                st.plotly_chart(fig)
            else:
                st.info("Aucun frais implicite détecté (net ≥ 0).")

            # Bouton pour exporter CSV résumé
            csv = summary_df.to_csv(index=False).encode("utf-8")
            st.download_button(label="Télécharger le résumé en CSV", data=csv, file_name="résumé_flows.csv", mime="text/csv")
