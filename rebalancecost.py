import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Analyseur de Rebalance", layout="wide")
st.title("🔍 Analyseur de Transaction Rebalance (Texte Collé)")

input_text = st.text_area("Collez ici le texte brut de la transaction :", height=600)

# 🧠 Parsing du texte collé
def parse_text(text):
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    data = []
    i = 0

    while i < len(lines):
        if lines[i].startswith("From"):
            from_address = lines[i + 1]
            to_address = "Unknown"
            amount = 0.0
            usd = 0.0
            token = "Unknown"

            if i + 2 < len(lines) and lines[i + 2].startswith("To"):
                to_address = lines[i + 3]

            if i + 4 < len(lines) and lines[i + 4].startswith("For"):
                amount_str = lines[i + 5].strip()
                try:
                    amount = float(amount_str)
                except ValueError:
                    amount = 0.0

            if i + 6 < len(lines):
                usd_match = re.search(r"\(\$(.*?)\)", lines[i + 6])
                if usd_match:
                    try:
                        usd = float(usd_match.group(1))
                    except ValueError:
                        usd = 0.0

            # Recherche du token (souvent juste avant "From")
            token_line = lines[i - 1] if i > 0 else "Unknown"
            token_match = re.search(r"\((.*?)\)", token_line)
            token = token_match.group(1) if token_match else token_line

            data.append({
                "Token": token,
                "From": from_address,
                "To": to_address,
                "Amount": amount,
                "USD": usd
            })

            i += 7
        else:
            i += 1

    return pd.DataFrame(data)

# 💡 Calcul des entrées/sorties nettes
def calculate_token_flows(df):
    tokens = df['Token'].unique()
    flow_data = []

    for token in tokens:
        token_df = df[df['Token'] == token]
        total_in = token_df['USD'][token_df['To'] != "Unknown"].sum()
        total_out = token_df['USD'][token_df['From'] != "Unknown"].sum()
        net = total_in - total_out

        flow_data.append({
            "Token": token,
            "Total reçu (USD)": round(total_in, 2),
            "Total envoyé (USD)": round(total_out, 2),
            "Net (USD)": round(net, 2)
        })

    return pd.DataFrame(flow_data)

# ✅ Affichage
if input_text:
    try:
        df = parse_text(input_text)

        st.subheader("📋 Détails des transferts détectés")
        st.dataframe(df, use_container_width=True)

        st.subheader("💰 Résumé des flux (globaux)")

        total_in = df['USD'][df['To'] != "Unknown"].sum()
        total_out = df['USD'][df['From'] != "Unknown"].sum()
        net = total_in - total_out

        col1, col2, col3 = st.columns(3)
        col1.metric("Total sortant", f"${total_out:.2f}")
        col2.metric("Total entrant", f"${total_in:.2f}")
        col3.metric("Net", f"${net:.2f}", delta=f"{net:.2f}")

        st.subheader("📊 Répartition par token")
        chart = df.groupby("Token")["USD"].sum().sort_values(ascending=False)
        st.bar_chart(chart)

        # 🔎 Calcul par token
        st.subheader("🧾 Analyse par token (net des flux)")
        flows_df = calculate_token_flows(df)
        st.dataframe(flows_df, use_container_width=True)

        # ⬇️ Export CSV
        st.subheader("⬇️ Export des données")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger transferts CSV", data=csv, file_name="transferts.csv", mime='text/csv')

        csv2 = flows_df.to_csv(index=False).encode('utf-8')
        st.download_button("Télécharger analyse flux CSV", data=csv2, file_name="flux_token.csv", mime='text/csv')

    except Exception as e:
        st.error(f"Erreur lors du parsing : {e}")
