import streamlit as st
import joblib
import pandas as pd
from utils import clean_text, fetch_text_from_url
import os

# Page Config
st.set_page_config(page_title="Fake News Detector", page_icon="📰", layout="centered")

# Load Model & Vectorizer
@st.cache_resource
def load_model():
    model_path = 'model/fake_news_model.pkl'
    vectorizer_path = 'model/tfidf_vectorizer.pkl'
    
    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        return None, None
        
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    return model, vectorizer

model, vectorizer = load_model()

# Header
st.title("📰 Fake News Detection System")
st.markdown("""
This system uses Machine Learning to detect if a news article is **Real** or **Fake**.
It provides a **Confidence Score** based on the prediction probability.
""")

if model is None:
    st.error("Model not found! Please run `python train_model.py` first to train the model.")
else:
    # Sidebar
    st.sidebar.header("Input Method")
    input_method = st.sidebar.radio("Choose how to input news:", ("Paste Text", "Enter Headline", "Article URL"))
    
    user_input = ""
    
    if input_method == "Paste Text":
        st.subheader("📝 Paste News Content")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load Real News Sample"):
                st.session_state['text_input'] = "The finance ministry released a statement regarding the new tax slabs applicable from next year. The government aims to reduce the burden on the middle class."
        with col2:
            if st.button("Load Fake News Sample"):
                st.session_state['text_input'] = "A local man claims to have eaten 500 burgers in a single meal, doctors are baffled. The man, known as 'Burger King', says he felt fine afterwards."
        
        # Use session state to handle button clicks updating text area
        if 'text_input' not in st.session_state:
            st.session_state['text_input'] = ""
            
        user_input = st.text_area("Paste the full article text here:", value=st.session_state['text_input'], height=200)
        
    elif input_method == "Enter Headline":
        st.subheader("📢 Enter News Headline")
        user_input = st.text_input("Enter the news headline here:")
        
    elif input_method == "Article URL":
        st.subheader("🔗 Enter Article URL")
        url = st.text_input("Paste the link to the news article:")
        if url:
            with st.spinner("Fetching article content..."):
                extracted_text, error = fetch_text_from_url(url)
                if error:
                    st.error(f"Error fetching URL: {error}")
                else:
                    st.success("Article fetched successfully!")
                    with st.expander("View Extracted Text"):
                        st.write(extracted_text)
                    user_input = extracted_text

    # Prediction Logic
    if st.button("Predict Authenticity"):
        if not user_input:
            st.warning("Please provide some text to analyze.")
        else:
            with st.spinner("Analyzing..."):
                # 1. Preprocess
                cleaned_text = clean_text(user_input)
                
                # 2. Vectorize
                input_vector = vectorizer.transform([cleaned_text])
                
                # 3. Predict
                prediction = model.predict(input_vector)[0]
                probabilities = model.predict_proba(input_vector)[0]
                
                # Real=0, Fake=1
                real_prob = probabilities[0]
                fake_prob = probabilities[1]
                
                # Confidence Threshold
                confidence = max(real_prob, fake_prob)
                
                if confidence < 0.60:
                    result = "UNCERTAIN"
                    color = "orange"
                    st.warning("The model is not confident enough to classify this text definitively.")
                elif prediction == 1:
                    result = "FAKE NEWS"
                    color = "red"
                else:
                    result = "REAL NEWS"
                    color = "green"
                
                # Display Results
                st.markdown("---")
                st.subheader("Prediction Result:")
                st.markdown(f"<h1 style='text-align: center; color: {color};'>{result}</h1>", unsafe_allow_html=True)
                
                st.markdown(f"### Confidence: **{confidence*100:.2f}%**")
                
                # Progress bars for visualization
                st.write("Probability Breakdown:")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Real Probability", f"{real_prob*100:.2f}%")
                    st.progress(real_prob)
                with col2:
                    st.metric("Fake Probability", f"{fake_prob*100:.2f}%")
                    st.progress(fake_prob)

    # Footer / About
    st.markdown("---")
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        1. **Text Preprocessing**: The system cleans the text (removes punctuation, stopwords, etc.).
        2. **Vectorization**: Uses **TF-IDF** to convert text into numbers.
        3. **Prediction**: A **Passive Aggressive Classifier** analyzes the features.
        4. **Confidence Score**: The model's `predict_proba` function (calibrated) gives the certainty percentage.
        """)

