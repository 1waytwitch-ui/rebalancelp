import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Analyse Rebalance + Frais", layout="wide")
st.title("🔍 Analyseur de Transaction Rebalance (avec adresse et frais)")

st.markdown("Collez ci-dessous le texte brut de la transaction. Optionnellement, entrez votre adresse wallet pour calculer les flux réels (entrants, sortants, net).")

# 🎯 Inputs utilisateur
wallet_address = st.text_input("Adresse Ethereum de votre wallet (0x...)", placeholder="0xVotreAdresse")
gas_fee_input = st.text_input("Frais de gas (en USD, optionnel)", "0")
input_text = st.text_area("Collez ici le texte brut de la transaction :", height=600)

# Bouton pour lancer l’analyse
run_analysis = st.button("Analyser")

# 🧠 Parsing du texte
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

# 📊 Analyse de l'adresse utilisateur
def analyze_wallet_flows(df, wallet_address, gas_fee):
    wallet = wallet_address.lower()
    flows = []

    for token in df['Token'].unique():
        token_df = df[df['Token'] == token]
        sent = token_df[token_df['From'].str.lower() == wallet]['USD'].sum()
        received = token_df[token_df['To'].str.lower() == wallet]['USD'].sum()
        net = received - sent
        net_with_gas = net - gas_fee  # Pertes réelles

        flows.append({
            "Token": token,
            "Total reçu (USD)": round(received, 2),
            "Total envoyé (USD)": round(sent, 2),
            "Net (USD)": round(net, 2),
            "Net après gas (USD)": round(net_with_gas, 2)
        })

    return pd.DataFrame(flows)

# ▶️ Traitement si bouton pressé
if run_analysis and input_text:
    try:
        df = parse_text(input_text)
        st.subheader("📋 Détails des transferts détectés")
        st.dataframe(df, use_container_width=True)

        # Total global
        st.subheader("💰 Résumé global")
        total_in = df['USD'][df['To'] != "Unknown"].sum()
        total_out = df['USD'][df['From'] != "Unknown"].sum()
        net = total_in - total_out

        col1, col2, col3 = st.columns(3)
        col1.metric("Total sortant", f"${total_out:.2f}")
        col2.metric("Total entrant", f"${total_in:.2f}")
        col3.metric("Net brut", f"${net:.2f}", delta=f"{net:.2f}")

        st.subheader("📊 Répartition globale par token")
        st.bar_chart(df.groupby("Token")["USD"].sum())

        # 🎯 Analyse spécifique si adresse donnée
        try:
            gas_fee = float(gas_fee_input)
        except ValueError:
            gas_fee = 0.0

        if wallet_address.startswith("0x") and len(wallet_address) == 42:
            st.subheader("🧾 Analyse personnalisée pour le wallet")
            wallet_df = analyze_wallet_flows(df, wallet_address, gas_fee)
            st.dataframe(wallet_df, use_container_width=True)

            st.subheader("📉 Répartition des pertes (net après gas)")
            chart = wallet_df.set_index("Token")["Net après gas (USD)"]
            st.bar_chart(chart)
        else:
            st.info("Entrez une adresse valide pour voir l'analyse personnalisée.")

        # ⬇️ Exports
        st.subheader("⬇️ Export des données")
        st.download_button("Télécharger transferts CSV", df.to_csv(index=False), file_name="transferts.csv")
        if wallet_address.startswith("0x") and len(wallet_address) == 42:
            st.download_button("Télécharger analyse wallet CSV", wallet_df.to_csv(index=False), file_name="wallet_flux.csv")

    except Exception as e:
        st.error(f"Erreur lors de l'analyse : {e}")
