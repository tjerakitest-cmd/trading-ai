import streamlit as st
import google.generativeai as genai
import requests
from PIL import Image

# --- CONFIGURATION ---
GEMINI_KEY = "AIzaSyB7n7M-e3mCr8r6CEAnKPIStc-wFpguNE0"
FMP_KEY = "Qb1mjKvn5F2xVkkWOchTAzhUGz37JSsM"

# Configure AI
genai.configure(api_key=GEMINI_KEY)

# Page Setup
st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")

# CSS to make Chart Full Width & Remove Padding
st.markdown("""
    <style>
        .block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
        iframe {width: 100% !important; height: 800px !important;} 
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #EAB308;'>🚀 AI Trading Command Center</h2>", unsafe_allow_html=True)

# --- 1. BIG LIVE CHART (Height Fixed to 800px) ---
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
# Height parameter yahan zaroori hai
st.components.v1.html(tradingview_html, height=800)

st.divider()

# --- 2. AI & TOOLS SECTION ---
col1, col2 = st.columns([1, 1])

# Left Side: Chat Assistant
with col1:
    st.subheader("💬 AI Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if chat_input := st.chat_input("Puchiye: Gold ka trend kya hai?"):
        st.session_state.messages.append({"role": "user", "content": chat_input})
        with st.chat_message("user"):
            st.markdown(chat_input)
            
        with st.chat_message("assistant"):
            try:
                # 'gemini-1.5-flash' latest library ke sath hi chalta hai
                model = genai.GenerativeModel('gemini-1.5-flash')
                with st.spinner("AI soch raha hai..."):
                    res = model.generate_content(chat_input)
                    st.markdown(res.text)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
            except Exception as e:
                st.error(f"Error: {str(e)}. (Check requirements.txt update)")

# Right Side: Screenshot Analyzer
with col2:
    st.subheader("🖼️ Screenshot Analyzer")
    uploaded_file = st.file_uploader("Upload Chart Image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Chart", use_container_width=True)
        
        if st.button("Analyze Now"):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                with st.spinner("Analyzing Strategy..."):
                    prompt = "Analyze this chart image for trading signals based on support/resistance and EMAs. Verdict: Buy or Sell?"
                    response = model.generate_content([prompt, img])
                    st.success("Analysis Report:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Analysis Failed: {str(e)}")

# --- 3. NEWS FEED ---
with st.expander("📢 Live News Updates", expanded=False):
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
                st.warning("News API Key limit reached. Try again tomorrow.")
        except:
            st.error("Connection failed.")
