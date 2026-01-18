import streamlit as st
import requests
import json
import time

# --- CONFIGURATION ---
API_KEY = "AIzaSyDW70sARpfWEN2PzFqa0kqF0nzUbXK9n3Q"
FMP_KEY = "Qb1mjKvn5F2xVkkWOchTAzhUGz37JSsM"

st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")

# CSS: Full Screen Chart Fix
st.markdown("""
    <style>
        .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
        iframe {width: 100% !important; height: 800px !important;} 
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #EAB308;'>🚀 AI Trading Command Center</h2>", unsafe_allow_html=True)

# --- SMART CONNECTION (ONLY YOUR AVAILABLE MODELS) ---
def get_gemini_response_smart(prompt):
    # Aapki Doctor List se verified models (Priority Order)
    models_to_try = [
        "gemini-2.5-flash",              # 1. Newest (Fastest & Empty Queue)
        "gemini-2.0-flash-lite-preview-02-05", # 2. Lite Version (Very High Limits)
        "gemini-2.0-flash-exp",          # 3. Experimental
        "gemini-2.0-flash"               # 4. Standard (Backup)
    ]
    
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    last_error = ""

    for model_name in models_to_try:
        try:
            # URL banao specific model ke liye
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
            
            # Request bhejo
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            
            if response.status_code == 200:
                # Success! Batao kaunsa model chala
                return f"✅ **(Connected: {model_name})**\n\n" + response.json()['candidates'][0]['content']['parts'][0]['text']
            
            elif response.status_code == 429:
                # Quota Full - Agla try karo
                # st.toast(f"{model_name} busy tha, switching...") # Optional notification
                time.sleep(0.5)
                continue
                
            else:
                last_error = f"{model_name} Error: {response.status_code}"
                continue
                
        except Exception as e:
            last_error = str(e)
            continue

    return f"❌ All Models Busy. Last Error: {last_error}. (1 min wait karke refresh karein)"

# --- 1. LIVE CHART ---
tradingview_html = """
    <div class="tradingview-widget-container" style="height:800px; width:100%;">
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
st.components.v1.html(tradingview_html, height=800)

st.divider()

# --- 2. AI & NEWS ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💬 AI Assistant (Gemini 2.5 Powered)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if chat_input := st.chat_input("Puchiye: Market ka trend kya hai?"):
        st.session_state.messages.append({"role": "user", "content": chat_input})
        with st.chat_message("user"):
            st.markdown(chat_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing with Gemini 2.5..."):
                res_text = get_gemini_response_smart(chat_input)
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
                st.warning("⚠️ API Limit. Showing Backup:")
                st.markdown("**Gold Spot** | Support: 2550 | Resistance: 2600")
        except:
            st.error("Connection failed.")
