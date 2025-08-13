# rebalance_analyzer.py

import streamlit as st
from web3 import Web3
import requests
import pandas as pd
from datetime import datetime

# ----------- CONFIG ----------
ETHERSCAN_API_KEY = "VOTRE_CLE_API_ETHERSCAN"
INFURA_URL = "https://mainnet.infura.io/v3/VOTRE_CLE_INFURA"
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
ETHERSCAN_API = "https://api.etherscan.io/api"
# -----------------------------

# ----------- FUNCTIONS ------------
def get_tx_receipt(tx_hash):
    return web3.eth.get_transaction_receipt(tx_hash)

def get_tx_details(tx_hash):
    return web3.eth.get_transaction(tx_hash)

def get_token_transfers(tx_hash):
    url = f"{ETHERSCAN_API}?module=account&action=tokentx&txhash={tx_hash}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url)
    return response.json().get("result", [])

def wei_to_eth(wei):
    return Web3.from_wei(int(wei), 'ether')

def usd_estimate(symbol, amount):
    # Approximate static prices (can be connected to CoinGecko or DefiLlama)
    price_dict = {
        "WETH": 4620,
        "USDC": 1,
        "ZORA": 4.62  # Exemple
    }
    return price_dict.get(symbol, 0) * float(amount)
# ----------------------------------

# ----------- STREAMLIT UI -----------
st.title("🔍 Analyseur de Transaction Rebalance (Krystal)")

tx_hash = st.text_input("Entrer le hash de transaction Ethereum (0x...)")

if tx_hash:
    try:
        tx = get_tx_details(tx_hash)
        receipt = get_tx_receipt(tx_hash)
        transfers = get_token_transfers(tx_hash)

        st.subheader("📦 Informations de base")
        st.write(f"De : `{tx['from']}`")
        st.write(f"À : `{tx['to']}`")
        st.write(f"Gas utilisé : {receipt['gasUsed']} units")
        st.write(f"Bloc : {tx['blockNumber']}")
        st.write(f"Timestamp : {datetime.fromtimestamp(web3.eth.get_block(tx['blockNumber'])['timestamp'])}")

        # Créer tableau des transferts
        df = pd.DataFrame(transfers)
        df['amount'] = df['value'].astype(float) / 10 ** df['tokenDecimal'].astype(int)
        df['usd'] = df.apply(lambda row: usd_estimate(row['tokenSymbol'], row['amount']), axis=1)
        df = df[['from', 'to', 'tokenSymbol', 'amount', 'usd']]

        st.subheader("🔁 Transferts détectés")
        st.dataframe(df)

        total_in = df[df['to'] == tx['from']]['usd'].sum()
        total_out = df[df['from'] == tx['from']]['usd'].sum()
        net = total_in - total_out

        st.subheader("📊 Résumé financier")
        st.write(f"Total envoyé : **{total_out:.2f} $**")
        st.write(f"Total reçu : **{total_in:.2f} $**")
        st.write(f"Net : **{net:+.2f} $**")

        st.subheader("📉 Graphique des flux")
        chart_df = df.groupby('tokenSymbol')['usd'].sum().reset_index()
        st.bar_chart(chart_df.set_index('tokenSymbol'))

    except Exception as e:
        st.error(f"Erreur lors de l'analyse : {e}")
