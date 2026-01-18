import streamlit as st
import google.generativeai as genai
import requests
from PIL import Image

# --- CONFIGURATION (Free Keys) ---
GEMINI_KEY = "AIzaSyB7n7M-e3mCr8r6CEAnKPIStc-wFpguNE0"
FMP_KEY = "Qb1mjKvn5F2xVkkWOchTAzhUGz37JSsM"

# Setup AI Brain
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Page Look
st.set_page_config(page_title="AI Financial Assistant", layout="wide")

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center; color: #EAB308;'>💰 AI Trading & Financial Command Center</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>News Alerts | Chart Analysis | Abhay Patil Logic</p>", unsafe_allow_html=True)

# --- MAIN DASHBOARD (2 Columns) ---
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("🖼️ Chart & News Analysis")
    uploaded_file = st.file_uploader("Apna Chart Upload Karein", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Analyzing this chart...", use_container_width=True)
        
        if st.button("Analyze Current Setup"):
            with st.spinner("AI Chart aur News ko combine kar raha hai..."):
                prompt = """
                Tum ek professional financial assistant ho. Is chart ko dekho aur 'Abhay Patil' ke logic (CPR aur 20/50 EMA) se analyze karo.
                Batao ki trend kaisa hai, kya price support/resistance par hai, aur koi rejection candle dikh rahi hai? 
                Saath hi ye bhi batao ki current news ke hisab se kya probability hai.
                """
                response = model.generate_content([prompt, img])
                st.info(response.text)

with col2:
    st.subheader("💬 AI Assistant Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Puchiye, 'Gold ka support kahan hai?'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# --- BOTTOM SECTION: LIVE NEWS ---
st.divider()
st.subheader("📢 Real-time Economic News")
if st.button("Check Market News Impact"):
    try:
        url = f"https://financialmodelingprep.com/api/v3/economic_calendar?apikey={FMP_KEY}"
        data = requests.get(url).json()[:8]
        for event in data:
            with st.expander(f"📌 {event['event']} ({event['currency']}) - Impact: {event['impact']}"):
                st.write(f"Actual: {event['actual']} | Forecast: {event['estimate']}")
                if event['currency'] == "USD":
                    st.warning("Gold Traders: Watch out for USD volatility!")
    except:
        st.error("News load nahi ho pa rahi hai.")