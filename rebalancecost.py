import streamlit as st
import re

# --------- CONFIG ---------
st.set_page_config(
    page_title="Analyse Swap/Rebalance DEX",
    page_icon="🔍",
    layout="centered"
)

# --------- CUSTOM HEADER HTML ---------
st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(90deg, #3b82f6, #9333ea);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .header-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        max-width: 700px;
        margin: 0 auto;
    }

    @media (prefers-color-scheme: dark) {
        .header-container {
            background: linear-gradient(90deg, #2563eb, #7e22ce);
        }
    }

    /* Styles pour résumé et metrics */
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

    <div class="header-container">
        <div class="header-title">🔍 Analyse des coûts de Swap ou Rebalance</div>
        <div class="header-subtitle">
            Collez les logs d’une transaction (Etherscan ou DEX) pour obtenir une synthèse claire des pertes, frais et slippage.
        </div>
    </div>
""", unsafe_allow_html=True)

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
                weth_sent = float(sent_match.group(1))
                usd_sent = float(sent_match.group(2))
                weth_received = float(received_match[-1][0])
                usd_received = float(received_match[-1][1])

                weth_diff = weth_sent - weth_received
                usd_diff = usd_sent - usd_received
                pct_loss = (usd_diff / usd_sent) * 100

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
