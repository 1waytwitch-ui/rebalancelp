import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analyse Transaction Wallet", layout="wide")
st.title("🔍 Analyseur de transaction avec calcul automatique des frais")

# Input adresse wallet + texte
wallet_address = st.text_input("Adresse Ethereum de votre wallet (0x...)", placeholder="0xVotreAdresse")
input_text = st.text_area("Collez ici le texte brut de la transaction :", height=600)

run_analysis = st.button("Analyser")

def parse_text(text):
    # Parsing du texte, on extrait lignes From / To / Amount / USD
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    data = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("From"):
            try:
                from_address = lines[i+1]
                to_address = lines[i+3] if i+3 < len(lines) else "Unknown"
                amount = float(lines[i+5]) if i+5 < len(lines) else 0.0
                usd = 0.0
                # Extraction USD (ex: (123.45$)) dans la ligne i+6
                if i+6 < len(lines):
                    usd_str = lines[i+6]
                    # on cherche un nombre dans la ligne
                    import re
                    match = re.search(r"(\d+(\.\d+)?)\$", usd_str)
                    if match:
                        usd = float(match.group(1))
                # Pour le token, on prend la ligne avant "From" si elle contient le token entre parenthèses
                token_line = lines[i-1] if i-1 >= 0 else "Unknown"
                import re
                token_match = re.search(r"\((.*?)\)", token_line)
                token = token_match.group(1) if token_match else token_line
                data.append({
                    "Token": token,
                    "From": from_address,
                    "To": to_address,
                    "Amount": amount,
                    "USD": usd
                })
            except Exception as e:
                # ignore lines mal formées
                pass
            i += 7
        else:
            i += 1
    return pd.DataFrame(data)

def analyze_flows(df, wallet):
    wallet = wallet.lower()
    tokens = df["Token"].unique()
    results = []
    for token in tokens:
        df_token = df[df["Token"]==token]
        total_sent = df_token[df_token["From"].str.lower()==wallet]["USD"].sum()
        total_received = df_token[df_token["To"].str.lower()==wallet]["USD"].sum()
        net = total_received - total_sent
        results.append({
            "Token": token,
            "Total envoyé (USD)": round(total_sent, 4),
            "Total reçu (USD)": round(total_received, 4),
            "Net (USD)": round(net, 4),
            "Frais implicites (USD)": round(-net if net < 0 else 0, 4)
        })
    return pd.DataFrame(results)

if run_analysis:
    if not wallet_address or not wallet_address.startswith("0x") or len(wallet_address) != 42:
        st.error("Merci d'entrer une adresse Ethereum valide (commence par 0x et fait 42 caractères)")
    elif not input_text:
        st.error("Merci de coller le texte brut de la transaction")
    else:
        df = parse_text(input_text)
        if df.empty:
            st.warning("Aucune donnée détectée dans le texte. Vérifiez le format.")
        else:
            st.subheader("📋 Détails des transferts détectés")
            st.dataframe(df, use_container_width=True)

            st.subheader("💰 Résumé des flux pour l'adresse :")
            flows_df = analyze_flows(df, wallet_address)
            st.dataframe(flows_df, use_container_width=True)

            total_sent = flows_df["Total envoyé (USD)"].sum()
            total_received = flows_df["Total reçu (USD)"].sum()
            total_net = total_received - total_sent
            total_fees = -total_net if total_net < 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Total envoyé", f"${total_sent:.4f}")
            col2.metric("Total reçu", f"${total_received:.4f}")
            col3.metric("Frais implicites estimés", f"${total_fees:.4f}")

            st.subheader("📊 Répartition des frais implicites par token")
            # On affiche les frais implicites par token uniquement si > 0
            fees_chart_data = flows_df[flows_df["Frais implicites (USD)"] > 0][["Token", "Frais implicites (USD)"]].set_index("Token")
            if fees_chart_data.empty:
                st.info("Aucun frais implicite détecté (net >= 0).")
            else:
                st.bar_chart(fees_chart_data)
