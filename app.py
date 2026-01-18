import streamlit as st
import google.generativeai as genai
import requests
from PIL import Image

# --- CONFIGURATION ---
# Aapki API Keys (Jo aapne di thi)
GEMINI_KEY = "AIzaSyB7n7M-e3mCr8r6CEAnKPIStc-wFpguNE0"
FMP_KEY = "Qb1mjKvn5F2xVkkWOchTAzhUGz37JSsM"

# AI Model Setup (Error Fixing Logic)
genai.configure(api_key=GEMINI_KEY)
# Hum 'gemini-1.5-flash' use karenge jo free aur fast hai.
# Agar ye error de, toh code automatic handle karega.
MODEL_NAME = 'gemini-1.5-flash'

st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")

# --- CSS HACK FOR FULL WIDTH ---
st.markdown("""
    <style>
        .block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
        iframe {width: 100% !important; height: 800px !important;} 
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #EAB308; margin-bottom: 10px;'>🚀 AI Trading Command Center</h2>", unsafe_allow_html=True)

# --- 1. BIG LIVE CHART (Cinematic Mode) ---
st.subheader("📊 Live Market Terminal")
# Height ko 800px kar diya hai taaki chart bada dikhe
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
          "hide_side_toolbar": false,
          "container_id": "tradingview_any"
        });
        </script>
    </div>
"""
st.components.v1.html(tradingview_html, height=800)

st.divider()

# --- 2. AI & TOOLS SECTION ---
col1, col2 = st.columns([1, 1])

# Left Side: Chat Assistant
with col1:
    st.subheader("💬 AI Assistant (Abhay Patil Logic)")
    
    # Session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if chat_input := st.chat_input("Puchiye: Gold ka trend kya hai?"):
        st.session_state.messages.append({"role": "user", "content": chat_input})
        with st.chat_message("user"):
            st.markdown(chat_input)
            
        with st.chat_message("assistant"):
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                with st.spinner("AI soch raha hai..."):
                    res = model.generate_content(chat_input)
                    st.markdown(res.text)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
            except Exception as e:
                error_msg = f"Error: {str(e)}. (Model ya Key issue ho sakta hai)"
                st.error(error_msg)

# Right Side: Screenshot Analyzer
with col2:
    st.subheader("🖼️ Screenshot Analyzer")
    st.info("Agar chart par koi khaas setup dikhe, toh screenshot upload karein.")
    uploaded_file = st.file_uploader("Upload Chart Image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Chart", use_container_width=True)
        
        if st.button("Analyze Now"):
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                with st.spinner("Analyzing CPR & EMAs..."):
                    prompt = "You are a pro trader following Abhay Patil's strategy. Analyze this chart image. Look for CPR, 20/50 EMAs, and candlestick patterns. Give a clear BUY, SELL, or WAIT verdict."
                    response = model.generate_content([prompt, img])
                    st.success("Analysis Report:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Analysis Failed: {str(e)}")

# --- 3. NEWS FEED ---
with st.expander("📢 Live News Updates (Click to Open)", expanded=False):
    if st.button("Refresh News"):
        try:
            url = f"https://financialmodelingprep.com/api/v3/economic_calendar?apikey={FMP_KEY}"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()[:8]
                for n in data:
                    color = "red" if "High" in n.get('impact', '') else "gray"
                    st.markdown(f"**{n['event']}** ({n['currency']}) | Impact: :{color}[{n['impact']}] | Actual: {n['actual']}")
            else:
                st.warning("News API limit reached or busy. Try later.")
        except:
            st.error("Connection failed.")
