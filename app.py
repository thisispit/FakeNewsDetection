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
        user_input = st.text_area("Paste the full article text here:", height=200)
        
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
                
                # prob[0] = Real, prob[1] = Fake (Based on our training mapping: Real=0, Fake=1)
                # However, let's double check the mapping logic from train_model.py
                # In train_model.py we did: {'FAKE': 1, 'REAL': 0}
                # So class 0 is Real, class 1 is Fake.
                
                real_prob = probabilities[0]
                fake_prob = probabilities[1]
                
                if prediction == 1:
                    result = "FAKE NEWS"
                    confidence = fake_prob
                    color = "red"
                else:
                    result = "REAL NEWS"
                    confidence = real_prob
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
        3. **Prediction**: A **Logistic Regression** model analyzes the features.
        4. **Confidence Score**: The model's `predict_proba` function gives the certainty percentage.
        """)

