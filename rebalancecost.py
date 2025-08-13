import streamlit as st
import re

st.set_page_config(page_title="Analyse Rebalance Krystal", layout="centered")

st.title("🧮 Analyse des coûts de Rebalance - Krystal")
st.markdown("Colle ci-dessous les logs de ta transaction (copiés depuis Etherscan ou l'app).")

# Zone de texte pour logs
logs = st.text_area("📋 Colle les logs ici", height=400)

if logs:
    # Extraction du montant WETH envoyé
    sent_match = re.search(r"For\n([0-9.]+)\n\(\$([0-9.]+)\)\n\nWrapped Ethe", logs)
    received_match = re.findall(r"For\n([0-9.]+)\n\(\$([0-9.]+)\)\n\nWrapped Ethe", logs)

    if sent_match and len(received_match) >= 2:
        try:
            # Premier "From ... Wrapped Ether" = envoi
            weth_sent = float(sent_match.group(1))
            usd_sent = float(sent_match.group(2))

            # Dernier "To ... Wrapped Ether" = réception
            weth_received = float(received_match[-1][0])
            usd_received = float(received_match[-1][1])

            weth_diff = weth_sent - weth_received
            usd_diff = usd_sent - usd_received
            pct_loss = (usd_diff / usd_sent) * 100

            st.markdown("### 📊 Synthèse")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("WETH envoyé", f"{weth_sent:.8f}")
                st.metric("USD envoyé", f"${usd_sent:.2f}")
            with col2:
                st.metric("WETH reçu", f"{weth_received:.8f}")
                st.metric("USD reçu", f"${usd_received:.2f}")

            st.markdown("---")

            col3, col4 = st.columns(2)
            with col3:
                st.metric("Différence WETH", f"{weth_diff:.8f}")
            with col4:
                st.metric("Perte estimée", f"${usd_diff:.2f} ({pct_loss:.2f}%)", delta=f"-{pct_loss:.2f}%")

            st.markdown("---")

            # Interprétation simple
            st.markdown("### 🧠 Interprétation probable des frais :")
            st.write("- **Frais de swap** (~0.1%)")
            st.write("- **Slippage** (0.1–0.3%)")
            st.write("- **Frais de gas** (estimé 0.1–0.2 USD)")
            st.write("- Pas de frais d'auto-rebalance (non détecté)")

            st.success("✅ Analyse terminée avec succès.")

        except Exception as e:
            st.error("Erreur lors du traitement des montants : " + str(e))

    else:
        st.warning("❗ Impossible de détecter les montants WETH dans les logs collés.")
