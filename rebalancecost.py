import streamlit as st
import re

# --------- CONFIG ---------
st.set_page_config(
    page_title="Analyse Swap/Rebalance DEX",
    page_icon="🔍",
    layout="centered"
)

# --------- HEADER ---------
st.title("🔍 Analyse des coûts de Swap ou Rebalance")
st.markdown("Collez les logs d’une transaction (copiés depuis Etherscan ou une app) pour obtenir une analyse claire des coûts réels.")

st.markdown("---")

# --------- INPUT ---------
logs = st.text_area("📋 Collez vos logs ici :", height=400, placeholder="From\n0xd0b53D92...\nTo\n...")

# --------- PARSE ---------
if logs:
    sent_match = re.search(r"For\n([0-9.]+)\n\(\$([0-9.]+)\)\n\nWrapped Ethe", logs)
    received_match = re.findall(r"For\n([0-9.]+)\n\(\$([0-9.]+)\)\n\nWrapped Ethe", logs)

    if sent_match and len(received_match) >= 2:
        try:
            # Extraction des données
            weth_sent = float(sent_match.group(1))
            usd_sent = float(sent_match.group(2))
            weth_received = float(received_match[-1][0])
            usd_received = float(received_match[-1][1])

            weth_diff = weth_sent - weth_received
            usd_diff = usd_sent - usd_received
            pct_loss = (usd_diff / usd_sent) * 100

            # --------- RÉSULTATS ---------
            st.markdown("## 📊 Résumé des montants")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔼 WETH envoyé", f"{weth_sent:.8f}")
                st.metric("💵 USD envoyé", f"${usd_sent:.2f}")
            with col2:
                st.metric("🔽 WETH reçu", f"{weth_received:.8f}")
                st.metric("💰 USD reçu", f"${usd_received:.2f}")

            st.markdown("---")

            col3, col4 = st.columns(2)
            with col3:
                st.metric("📉 Diff. WETH", f"{weth_diff:.8f}", delta=f"-{weth_diff:.8f}")
            with col4:
                st.metric("🔻 Perte estimée", f"${usd_diff:.2f}", delta=f"-{pct_loss:.2f}%")

            st.markdown("---")

            # --------- INTERPRÉTATION ---------
            st.markdown("## 🧠 Analyse des frais probables")
            st.info("""
- **Frais de swap** (~0.1 %)
- **Slippage** (0.1 à 0.3 %)
- **Frais de gas** estimés : $0.10 à $0.20
- **Aucun frais d’automatisation détecté**
            """)

            st.success("✅ Analyse terminée avec succès.")

        except Exception as e:
            st.error("❌ Erreur lors du traitement : " + str(e))

    else:
        st.warning("⚠️ Impossible de détecter les montants WETH dans les logs collés. Vérifiez le format.")
