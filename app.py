import streamlit as st
import requests

# --- DIAGNOSTIC TOOL ---
API_KEY = "AIzaSyDW70sARpfWEN2PzFqa0kqF0nzUbXK9n3Q" # Aapki Nayi Key

st.set_page_config(page_title="API Doctor", layout="wide")
st.title("👨‍⚕️ API Key Diagnosis Report")

if st.button("Check My API Key Health"):
    st.write("Checking connection with Google...")
    
    # 1. Test: Kya Key Valid hai? Aur kaunse models available hain?
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            st.success("✅ SUCCESS! API Key bilkul sahi hai.")
            st.write("### Aapke liye Available Models:")
            
            # Models ki list print karein
            if 'models' in data:
                found_models = []
                for m in data['models']:
                    # Hamein sirf generateContent wale models chahiye
                    if "generateContent" in m['supportedGenerationMethods']:
                        name = m['name'].replace("models/", "")
                        found_models.append(name)
                        st.code(name)
                
                st.info(f"Total {len(found_models)} models mile. Hum '{found_models[0]}' use karenge.")
            else:
                st.warning("Key sahi hai par models ki list khali hai.")
        else:
            st.error("❌ FAILURE: API Key kaam nahi kar rahi.")
            st.write(f"**Error Code:** {response.status_code}")
            st.json(data) # Ye error ka asli reason batayega
            
    except Exception as e:
        st.error(f"Connection Error: {e}")
