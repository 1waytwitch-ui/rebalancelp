import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Analyseur de Rebalance", layout="wide")

st.title("🔍 Analyseur de Transaction Rebalance (Texte Collé)")

input_text = st.text_area("Collez ici le texte brut de la transaction :", height=600)

# ---------------------- PARSING -------------------------

def parse_text(text):
    lines = text.strip().split("\n")
    data = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("From"):
            from_address = lines[i + 1].strip()
            to_line = lines[i + 2].strip()
            to_address = lines[i + 3].strip()

            for_line = lines[i + 4].strip()
            amount_match = re.search(r"For\n([0-9\.Ee+-]+)", "\n".join(lines[i+4:i+6]))
            usd_match = re.search(r"\(\$(.*?)\)", "\n".join(lines[i+4:i+6]))

            amount = float(amount_match.group(1)) if amount_match else 0
            usd = float(usd_match.group(1)) if usd_match else 0

            # Cherche le token sur la ligne suivante (ou actuelle si formaté différemment)
            token_line = lines[i - 1].strip() if i > 0 else "Unknown"
            token_match = re.search(r"\((.*?)\)", token_line)
            token = token_match.group(1) if token_match else token_line

            data.append({
                "Token": token,
                "From": from_address,
                "To": to_address,
                "Amount": amount,
                "USD": usd
            })

            i += 6  # Sauter au bloc suivant
        else:
            i += 1

    return pd.DataFrame(data)

# ---------------------- INTERFACE -------------------------

if input_text:
    try:
        df = parse_text(input_text)

        st.subheader("📋 Détails des transferts détectés")
        st.dataframe(df, use_container_width=True)

        st.subheader("💰 Résumé des flux")
        total_in = df.groupby('To')['USD'].sum().sum()
        total_out = df.groupby('From')['USD'].sum().sum()
        net = total_in - total_out

        col1, col2, col3 = st.columns(3)
        col1.metric("Total sortant", f"${total_out:.2f}")
        col2.metric("Total entrant", f"${total_in:.2f}")
        col3.metric("Net", f"${net:.2f}", delta=f"{net:.2f}")

        st.subheader("📊 Répartition par token")
        chart = df.groupby("Token")["USD"].sum().sort_values(ascending=False)
        st.bar_chart(chart)

    except Exception as e:
        st.error(f"Erreur de parsing : {e}")
