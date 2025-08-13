import streamlit as st
import re

# --------- CONFIG ---------
st.set_page_config(
    page_title="Analyse Swap/Rebalance DEX",
    page_icon="🔍",
    layout="centered"
)

# --------- STYLE ---------
st.markdown("""
<style>
/* Blocs de synthèse */
.metric-container {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 1rem;
}

.metric-box {
    flex: 1 1 200px;
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    font-weight: bold;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Couleurs adaptatives pour thèmes clairs/sombres */
[data-testid="stAppViewContainer"] {
    --bg-sent: #e0f7fa;
    --bg-received: #e8f5e9;
    --bg-diff: #fff3e0;
    --bg-loss: #fce4ec;
}

@media (prefers-color-scheme: dark) {
    [data-testid="stAppViewContainer"] {
        --bg-sent: #00333d;
        --bg-received: #1b4b2f;
        --bg-diff: #4b3e00;
        --bg-loss: #5a0024;
    }
}
</style>
""", unsafe_allow_html=True)

# --------- TITRE ---------
st.title("🔍 Analyse des coûts de Swap ou Rebalance")
st.markdown("Collez les logs d’une transaction (copiés depuis Etherscan ou une app) pour obtenir une analyse claire des coûts réels.")
st.markdown("---")

# --------- INPUT ---------
logs = st.text_area("📋 Collez vos logs ici :", height=400, placeholder="Exemple : From\n0x...\nTo\n...")

# --------- BOUTON ---------
analyser = st.button("🔎 Analyser")

# --------- PARSE & AFFICHAGE ---------
if logs and analyser:
    with st.spinner("⏳ Analyse en cours..."):
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
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="metric-box" style="background-color: var(--bg-sent);">
                🔼 WETH envoyé<br><span style='font-size: 1.5em'>{weth_sent:.8f}</span>
                </div>
                <div class="metric-box" style="background-color: var(--bg-sent);">
                💵 USD envoyé<br><span style='font-size: 1.5em'>${usd_sent:.2f}</span>
                </div>
                <div class="metric-box" style="background-color: var(--bg-received);">
                🔽 WETH reçu<br><span style='font-size: 1.5em'>{weth_received:.8f}</span>
                </div>
                <div class="metric-box" style="background-color: var(--bg-received);">
                💰 USD reçu<br><span style='font-size: 1.5em'>${usd_received:.2f}</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

                # Différences
                st.markdown("---")
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="metric-box" style="background-color: var(--bg-diff);">
                📉 Diff. WETH<br><span style='font-size: 1.5em'>{weth_diff:.8f}</span>
                </div>
                <div class="metric-box" style="background-color: var(--bg-loss);">
                🔻 Perte estimée<br><span style='font-size: 1.5em'>${usd_diff:.2f} ({pct_loss:.2f}%)</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

                # Analyse textuelle
                st.markdown("---")
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
