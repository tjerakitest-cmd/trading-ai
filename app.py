import streamlit as st
import requests
import json

# --- CONFIGURATION ---
GEMINI_KEY = "AIzaSyB7n7M-e3mCr8r6CEAnKPIStc-wFpguNE0"
FMP_KEY = "Qb1mjKvn5F2xVkkWOchTAzhUGz37JSsM"

st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")

# --- CSS: FORCE FULL SCREEN CHART ---
st.markdown("""
    <style>
        .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 0.5rem; padding-right: 0.5rem;}
        iframe {width: 100% !important; height: 85vh !important;} 
    </style>
""", unsafe_allow_html=True)

# --- SMART CONNECT FUNCTION (TRY ALL MODELS) ---
def ask_gemini_smart(prompt):
    # Hum 3 alag-alag models try karenge jab tak ek chal na jaye
    models_to_try = [
        "gemini-1.5-flash", 
        "gemini-1.5-flash-latest", 
        "gemini-pro", 
        "gemini-1.0-pro"
    ]
    
    for model_name in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_KEY}"
            headers = {'Content-Type': 'application/json'}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=5)
            
            if response.status_code == 200:
                # Agar success ho gaya, toh answer return kardo aur loop tod do
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            
        except:
            continue # Agar fail hua toh agla model try karo
            
    return "Error: Koi bhi model connect nahi ho pa raha. Please naya API Key generate karein Google AI Studio se."

st.markdown("<h3 style='text-align: center; color: #EAB308; margin: 0; padding: 10px;'>🚀 AI Trading Command Center</h3>", unsafe_allow_html=True)

# --- 1. BIG LIVE CHART ---
tradingview_html = """
    <div class="tradingview-widget-container" style="height:85vh; width:100%;">
        <div id="tradingview_any"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true,
          "symbol": "FOREXCOM:XAUUSD",
          "interval": "15",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "toolbar_bg": "#f1f3f6",
          "enable_publishing": false,
          "allow_symbol_change": true,
          "details": true,
          "hotlist": true,
          "calendar": true,
          "container_id": "tradingview_any"
        });
        </script>
    </div>
"""
st.components.v1.html(tradingview_html, height=700)

st.divider()

# --- 2. AI & NEWS ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 AI Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if chat_input := st.chat_input("Puchiye: Market bullish hai ya bearish?"):
        st.session_state.messages.append({"role": "user", "content": chat_input})
        with st.chat_message("user"):
            st.markdown(chat_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Connecting to best available model..."):
                res_text = ask_gemini_smart(chat_input)
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})

with col2:
    st.subheader("📢 News Updates")
    if st.button("Refresh News"):
        try:
            url = f"https://financialmodelingprep.com/api/v3/economic_calendar?apikey={FMP_KEY}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()[:8]
                for n in data:
                    color = "red" if "High" in n.get('impact', '') else "gray"
                    st.markdown(f"**{n['event']}** ({n['currency']}) | {n['actual']}")
            else:
                st.warning("News API issue.")
        except:
            st.error("Connection failed.")
