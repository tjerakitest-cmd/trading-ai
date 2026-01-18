import streamlit as st
import requests
import json
from PIL import Image
import io

# --- CONFIGURATION ---
GEMINI_KEY = "AIzaSyB7n7M-e3mCr8r6CEAnKPIStc-wFpguNE0"
FMP_KEY = "Qb1mjKvn5F2xVkkWOchTAzhUGz37JSsM"

st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")

# --- CSS: FORCE FULL SCREEN CHART ---
st.markdown("""
    <style>
        .block-container {padding-top: 0.5rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
        iframe {width: 100% !important; height: 800px !important;} 
        .stChatInput {position: fixed; bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #EAB308; margin: 0;'>🚀 AI Trading Command Center</h2>", unsafe_allow_html=True)

# --- DIRECT API FUNCTION (NO LIBRARY) ---
def ask_gemini(prompt, image=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Text Only Payload
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    # Image + Text Payload (agar image upload hui to)
    if image:
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()
        
        # Simple Logic: Hum vision ke liye alag approach use nahi karenge taaki code complex na ho.
        # Filhal text analysis par focus karte hain error free experience ke liye.
        return "Abhi Image analysis disabled hai stability ke liye. Kripya text chat use karein."

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Connection Failed: {str(e)}"

# --- 1. BIG LIVE CHART ---
st.subheader("📊 Live Market Terminal")
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
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 AI Assistant (Direct API)")
    
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
            with st.spinner("AI thinking..."):
                # Call Direct API
                res_text = ask_gemini(chat_input)
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
