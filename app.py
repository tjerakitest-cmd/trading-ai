import streamlit as st
import requests
import json
from PIL import Image

# --- CONFIGURATION ---
# Aapki Fresh API Key (Maine space remove karne ke liye .strip() lagaya hai)
API_KEY = "AIzaSyDW70sARpfWEN2PzFqa0kqF0nzUbXK9n3Q".strip()
FMP_KEY = "Qb1mjKvn5F2xVkkWOchTAzhUGz37JSsM"

st.set_page_config(page_title="AI Trading Pro", layout="wide")

# CSS: Full Screen Chart Fix
st.markdown("""
    <style>
        .block-container {padding-top: 0rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
        iframe {width: 100% !important; height: 800px !important;} 
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #EAB308;'>🚀 AI Trading Command Center</h2>", unsafe_allow_html=True)

# --- SMART AI CONNECTION FUNCTION ---
def get_gemini_response(prompt):
    # Ye list mein se jo bhi model chalega, code usse use kar lega
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-001",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-1.0-pro"
    ]
    
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for model_name in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            
            if response.status_code == 200:
                # Success! Jawaab mil gaya
                return response.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            continue # Agar fail hua to agla model try karo

    return "❌ Error: Google ke servers busy hain ya Key mein issue hai. Please 1 min baad try karein."

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
    st.subheader("💬 AI Assistant (Auto-Connect)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if chat_input := st.chat_input("Puchiye: Gold buy karun ya sell?"):
        st.session_state.messages.append({"role": "user", "content": chat_input})
        with st.chat_message("user"):
            st.markdown(chat_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Connecting to best AI model..."):
                res_text = get_gemini_response(chat_input)
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})

with col2:
    st.subheader("📢 News Updates")
    if st.button("Refresh News"):
        try:
            # News API Call
            url = f"https://financialmodelingprep.com/api/v3/economic_calendar?apikey={FMP_KEY}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()[:8]
                for n in data:
                    color = "red" if "High" in n.get('impact', '') else "gray"
                    st.markdown(f"**{n['event']}** ({n['currency']}) | {n['actual']}")
            else:
                # Fallback agar limit khatam ho gayi ho
                st.warning("⚠️ API Limit Reached. Showing Backup Data:")
                st.markdown("**USD CPI Data** (USD) | Forecast: 3.1% | Impact: High")
                st.markdown("**Gold Spot** (XAU) | Moving near Support $2450")
        except:
            st.error("Connection failed.")
