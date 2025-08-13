import streamlit as st
import re


# --------- CONFIG ---------
st.set_page_config(
    page_title="Analyse Swap/Rebalance DEX",
    page_icon="📊",
    layout="centered"
)


# --------- CSS ---------
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
    .metric-box {
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #222;
        margin-bottom: 0.8rem;
    }
    /* Couleurs vives */
    .sent {
        background-color: #42a5f5;  /* bleu vif */
        color: white;
    }
    .received {
        background-color: #66bb6a;  /* vert vif */
        color: white;
    }
    .diff {
        background-color: #ffca28;  /* jaune vif */
        color: #333;
    }
    .loss {
        background-color: #ef5350;  /* rouge vif */
        color: white;
    }
    .info-box {
        background-color: #bbdefb;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        font-size: 1rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #222;
    }
    .success-box {
        background-color: #a5d6a7;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        font-size: 1rem;
        margin-bottom: 2rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #222;
    }
    .section-title {
        font-weight: 800;
        font-size: 1.9rem;
        margin-top: 2rem;
        margin-bottom: 0.3rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #222222;
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
if st.button("🔎 Analyser") and logs:

    with st.spinner("⏳ Analyse en cours..."):
        # Pattern générique pour trouver : "For\n<montant>\n(<USD>)\n\n<token>" 
        # ou "For\n<montant>\n\n<token>" sans USD
        pattern = re.compile(
            r"For\n([0-9.,]+)(?:\n\(\$?([\d.,]+)\))?\n\n([A-Za-z0-9]+)", 
            re.MULTILINE
        )

        matches = pattern.findall(logs)

        if not matches:
            st.warning("⚠️ Aucun token détecté dans les logs. Vérifiez le format.")
        else:
            # On va séparer les tokens envoyés et reçus selon l'ordre d'apparition:
            # Supposons que les tokens envoyés apparaissent en premier, puis reçus.
            # S'il y a une autre logique dans les logs, il faudra adapter.

            # Pour l'exemple, on considère la moitié première = tokens envoyés
            # deuxième moitié = tokens reçus
            half = len(matches) // 2
            sent_tokens = matches[:half]
            received_tokens = matches[half:]

            # Construit un dict pour avoir les tokens envoyés {symbol: {amount, usd}}
            sent_dict = {}
            for amt, usd, symbol in sent_tokens:
                amt = float(amt.replace(',', ''))
                usd_val = float(usd.replace(',', '')) if usd else 0.0
                sent_dict[symbol] = {"amount": amt, "usd": usd_val}

            # Idem pour tokens reçus
            received_dict = {}
            for amt, usd, symbol in received_tokens:
                amt = float(amt.replace(',', ''))
                usd_val = float(usd.replace(',', '')) if usd else 0.0
                received_dict[symbol] = {"amount": amt, "usd": usd_val}

            # Affichage
            st.markdown(f'<div class="section-title">📊 Résumé des montants</div>', unsafe_allow_html=True)

            # Envoyé
            for symbol, data in sent_dict.items():
                st.markdown(f"""
                <div class="metric-box sent">
                🔼 <b>{symbol} envoyé</b><br><span style='font-size: 1.6rem;'>{data["amount"]:.8f}</span><br>
                💵 <b>USD</b> : ${data["usd"]:.2f}
                </div>
                """, unsafe_allow_html=True)

            # Reçu
            for symbol, data in received_dict.items():
                st.markdown(f"""
                <div class="metric-box received">
                🔽 <b>{symbol} reçu</b><br><span style='font-size: 1.6rem;'>{data["amount"]:.8f}</span><br>
                💰 <b>USD</b> : ${data["usd"]:.2f}
                </div>
                """, unsafe_allow_html=True)

            # Calcul des différences USD
            total_sent_usd = sum(d["usd"] for d in sent_dict.values())
            total_received_usd = sum(d["usd"] for d in received_dict.values())
            diff_usd = total_sent_usd - total_received_usd
            pct_loss = (diff_usd / total_sent_usd) * 100 if total_sent_usd != 0 else 0

            st.markdown("---")
            st.markdown(f"""
            <div class="metric-box diff">
            📉 <b>Différence USD</b><br><span style='font-size: 1.6rem;'>${diff_usd:.2f}</span>
            </div>
            <div class="metric-box loss">
            🔻 <b>Perte estimée</b><br><span style='font-size: 1.6rem;'>${diff_usd:.2f} ({pct_loss:.2f} %)</span>
            </div>
            """ , unsafe_allow_html=True)

            # Analyse frais probable
            st.markdown("---")
            st.markdown(f'<div class="section-title">🧠 Analyse des frais probables</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="info-box">
            <ul>
            <li><b>Frais de swap</b> (~0.1 %)</li>
            <li><b>Slippage</b> (0.1 à 0.3 %)</li>
            <li><b>Frais de gas</b> estimés : 0.10 à 0.20 $</li>
            <li>Aucun frais d’automatisation détecté</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="success-box">✅ Analyse terminée avec succès.</div>', unsafe_allow_html=True)


# --- Signature discrète ---
st.markdown("<div class='signature'>© 1way</div>", unsafe_allow_html=True)
