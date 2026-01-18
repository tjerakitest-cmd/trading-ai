import streamlit as st
import google.generativeai as genai
import requests
from PIL import Image

# --- CONFIG ---
GEMINI_KEY = "AIzaSyB7n7M-e3mCr8r6CEAnKPIStc-wFpguNE0"
FMP_KEY = "Qb1mjKvn5F2xVkkWOchTAzhUGz37JSsM"

genai.configure(api_key=GEMINI_KEY)

st.set_page_config(page_title="AI Financial Assistant", layout="wide")

# --- HEADER ---
st.markdown("<h1 style='text-align: center; color: #EAB308;'>💰 My AI Trading Dashboard</h1>", unsafe_allow_html=True)

# --- 1. LIVE TRADINGVIEW WIDGET (NEW SECTION) ---
# Ye section aapko real-time chart dikhayega
st.subheader("📊 Live XAUUSD Chart (Real-time)")
tradingview_html = """
    <div class="tradingview-widget-container" style="height:500px; width:100%;">
        <div id="tradingview_gold"></div>
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
          "hide_top_toolbar": false,
          "save_image": true,
          "container_id": "tradingview_gold"
        });
        </script>
    </div>
"""
st.components.v1.html(tradingview_html, height=520)

# --- 2. AI ANALYSIS & CHAT ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("🖼️ Screenshot Analyzer")
    st.write("Live chart ke alawa agar koi specific setup analyze karna ho:")
    uploaded_file = st.file_uploader("Upload Chart Screenshot", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        if st.button("AI ko Analysis dikhao"):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "Analyze this chart image using Abhay Patil's strategy (CPR and 20/50 EMA). Tell me if it's a Buy, Sell, or Wait."
                response = model.generate_content([prompt, img])
                st.info(response.text)
            except Exception as e:
                st.error(f"AI Error: {e}")

with col2:
    st.subheader("💬 Assistant Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if chat_input := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": chat_input})
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(chat_input)
        st.session_state.messages.append({"role": "assistant", "content": res.text})
        st.rerun()

# --- 3. NEWS IMPACT ---
st.divider()
st.subheader("📢 Market News Impact")
if st.button("Check News Now"):
    try:
        url = f"https://financialmodelingprep.com/api/v3/economic_calendar?apikey={FMP_KEY}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()[:10]
            for n in data:
                with st.expander(f"{n['event']} ({n['currency']})"):
                    st.write(f"Impact: {n['impact']} | Actual: {n['actual']} | Forecast: {n['estimate']}")
        else:
            st.error("News API issue. Shayad key expire ho gayi hai.")
    except:
        st.error("Connection Error. Please try again.")
