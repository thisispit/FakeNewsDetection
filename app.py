import streamlit as st
import joblib
import pandas as pd
from utils import clean_text, fetch_text_from_url
from database import (init_database, insert_prediction, get_prediction_history, 
                     search_predictions, filter_predictions, insert_feedback, 
                     get_feedback_stats, get_prediction_stats)
from explainer import FakeNewsExplainer
from credibility import check_source_credibility
from export_utils import generate_pdf_report, create_csv_export, process_batch_csv
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# Page Config
st.set_page_config(page_title="Fake News Detector", page_icon="📰", layout="wide")

# Initialize Database
init_database()

# Load Model & Vectorizer
@st.cache_resource
def load_model():
    model_path = 'model/fake_news_model.pkl'
    vectorizer_path = 'model/tfidf_vectorizer.pkl'
    
    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        return None, None, None
        
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    
    # Initialize explainer
    explainer = FakeNewsExplainer(model, vectorizer)
    
    return model, vectorizer, explainer

model, vectorizer, explainer = load_model()

# Initialize session state
if 'current_prediction_id' not in st.session_state:
    st.session_state.current_prediction_id = None
if 'comparison_articles' not in st.session_state:
    st.session_state.comparison_articles = []

# Custom CSS for professional minimal UI
def apply_custom_css():
    st.markdown("""
    <style>
        /* Professional Minimal Dark Theme */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .stApp {
            background-color: #0a0a0a;
            color: #e8e8e8;
        }
        
        /* Typography */
        h1 {
            color: #ffffff;
            font-weight: 600;
            font-size: 2.2rem;
            margin-bottom: 0.5rem;
        }
        
        h2 {
            color: #f0f0f0;
            font-weight: 500;
            font-size: 1.5rem;
            margin-top: 2rem;
        }
        
        h3 {
            color: #e0e0e0;
            font-weight: 500;
            font-size: 1.2rem;
        }
        
        /* Buttons - Professional */
        .stButton>button {
            background-color: #ffffff;
            color: #0a0a0a;
            border: none;
            border-radius: 6px;
            padding: 0.6rem 1.5rem;
            font-weight: 500;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }
        
        .stButton>button:hover {
            background-color: #f0f0f0;
            box-shadow: 0 2px 8px rgba(255, 255, 255, 0.1);
        }
        
        /* Primary Action Button */
        .stButton>button[kind="primary"] {
            background-color: #4CAF50;
            color: white;
        }
        
        .stButton>button[kind="primary"]:hover {
            background-color: #45a049;
        }
        
        /* Download Buttons */
        .stDownloadButton>button {
            background-color: transparent;
            color: #e8e8e8;
            border: 1px solid #333333;
            border-radius: 6px;
            padding: 0.6rem 1.2rem;
            font-weight: 400;
            transition: all 0.2s ease;
        }
        
        .stDownloadButton>button:hover {
            border-color: #4CAF50;
            background-color: rgba(76, 175, 80, 0.1);
        }
        
        /* Input Fields */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            background-color: #141414;
            color: #e8e8e8;
            border: 1px solid #262626;
            border-radius: 6px;
            padding: 0.7rem;
            font-size: 0.95rem;
        }
        
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 0 1px #4CAF50;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #000000;
            border-right: 1px solid #1a1a1a;
        }
        
        [data-testid="stSidebar"] h2 {
            font-size: 1rem;
            font-weight: 500;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
        }
        
        /* Radio Buttons */
        .stRadio > label {
            font-weight: 500;
            color: #888;
        }
        
        .stRadio > div > label > div[data-testid="stMarkdownContainer"] p {
            font-size: 0.95rem;
            font-weight: 400;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #4CAF50;
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        [data-testid="stMetricLabel"] {
            color: #888;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Cards */
        .metric-card {
            background-color: #141414;
            border: 1px solid #1a1a1a;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
        
        /* Result Display */
        .result-container {
            background-color: #141414;
            border: 1px solid #1a1a1a;
            border-radius: 8px;
            padding: 2rem;
            margin: 2rem 0;
            text-align: center;
        }
        
        .result-badge {
            display: inline-block;
            padding: 0.6rem 2rem;
            border-radius: 6px;
            font-weight: 500;
            font-size: 1.1rem;
            margin: 1rem 0;
        }
        
        .badge-fake {
            background-color: #d32f2f;
            color: white;
        }
        
        .badge-real {
            background-color: #4CAF50;
            color: white;
        }
        
        .badge-uncertain {
            background-color: #ff9800;
            color: white;
        }
        
        /* Tables */
        .dataframe {
            border: 1px solid #1a1a1a;
            border-radius: 6px;
            overflow: hidden;
        }
        
        .dataframe th {
            background-color: #141414;
            color: #888;
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.05em;
            padding: 1rem;
            border-bottom: 1px solid #1a1a1a;
        }
        
        .dataframe td {
            background-color: #0a0a0a;
            color: #e8e8e8;
            padding: 0.9rem 1rem;
            border-bottom: 1px solid #141414;
        }
        
        /* Progress Bar */
        .stProgress > div > div > div {
            background-color: #4CAF50;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #141414;
            border: 1px solid #1a1a1a;
            border-radius: 6px;
            font-weight: 400;
        }
        
        .streamlit-expanderHeader:hover {
            border-color: #262626;
        }
        
        /* File Uploader */
        [data-testid="stFileUploader"] {
            background-color: #141414;
            border: 2px dashed #262626;
            border-radius: 8px;
            padding: 2rem;
        }
        
        /* Info/Success/Warning/Error */
        .stAlert {
            border-radius: 6px;
            border-left: 3px solid;
        }
        
        /* Divider */
        hr {
            border-color: #1a1a1a;
            margin: 2rem 0;
        }
        
        /* Links */
        a {
            color: #4CAF50;
        }
        
        a:hover {
            color: #66bb6a;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0a0a0a;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #262626;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #333333;
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            h1 {
                font-size: 1.8rem;
            }
            
            .stButton>button {
                width: 100%;
                margin-bottom: 0.5rem;
            }
            
            .result-container {
                padding: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

apply_custom_css()

# Header
st.title("Fake News Detector")
st.markdown("AI-powered news verification system")
st.markdown("---")

# Sidebar
st.sidebar.markdown("## MENU")
app_mode = st.sidebar.radio("", 
    ["🔍 Analyze Article", "📦 Batch Process", "⚖️ Compare Articles", "📜 History", "📊 Statistics"])

if model is None:
    st.error("⚠️ Model not found! Please run `python train_model.py` first to train the model.")
    st.stop()

# ===========================================
# SINGLE PREDICTION MODE
# ===========================================
if app_mode == "🔍 Analyze Article":
    st.header("Analyze Article")
    
    input_method = st.radio("Choose input method:", 
                           ("Paste Text", "Enter Headline", "Article URL"), 
                           horizontal=True)
    
    user_input = ""
    source_url = None
    
    if input_method == "Paste Text":
        st.subheader("📝 Paste News Content")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📗 Load Real News Sample"):
                st.session_state['text_input'] = "The finance ministry released a statement regarding the new tax slabs applicable from next year. The government aims to reduce the burden on the middle class."
        with col2:
            if st.button("📕 Load Fake News Sample"):
                st.session_state['text_input'] = "BREAKING: Local man claims to have eaten 500 burgers in ONE meal!!! Doctors are SHOCKED and can't explain it! Click here to find out his SECRET!"
        
        if 'text_input' not in st.session_state:
            st.session_state['text_input'] = ""
            
        user_input = st.text_area("Paste the full article text here:", 
                                 value=st.session_state['text_input'], height=200)
        
    elif input_method == "Enter Headline":
        st.subheader("📢 Enter News Headline")
        user_input = st.text_input("Enter the news headline here:")
        
    elif input_method == "Article URL":
        st.subheader("🔗 Enter Article URL")
        url = st.text_input("Paste the link to the news article:", placeholder="https://news-site.com/article-path", help="Enter a full URL including http:// or https://")
        source_url = url
        
        if url:
            with st.status("Fetching article content...", expanded=True) as status:
                st.write("Checking URL validity...")
                extracted_text, error = fetch_text_from_url(url)
                if error:
                    status.update(label=f"❌ Error: {error}", state="error", expanded=True)
                    st.error(f"Error fetching URL: {error}")
                else:
                    st.write("Analyzing source credibility...")
                    status.update(label="✅ Article fetched successfully!", state="complete", expanded=True)
                    st.success("✅ Article fetched successfully!")
                    
                    # Check source credibility
                    credibility = check_source_credibility(url)
                    if credibility['valid']:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.info(f"**Domain:** {credibility['domain']}")
                        with col2:
                            st.metric("Credibility Score", 
                                    f"{credibility['score']}/100",
                                    delta=credibility['reputation'].upper(),
                                    help="Score based on domain reputation and security. Higher is better.")
                        
                        if credibility['score'] < 50:
                            st.warning(f"⚠️ {credibility['details']}")
                        else:
                            st.success(f"✓ {credibility['details']}")
                    
                    with st.expander("View Extracted Text"):
                        st.write(extracted_text)
                    user_input = extracted_text

    # Prediction Button
    if st.button("🎯 Analyze Article", use_container_width=True, type="primary"):
        if not user_input:
            st.warning("⚠️ Please provide some text to analyze.")
        else:
            with st.status("🔍 Analyzing authenticity...", expanded=True) as status:
                st.write("Preprocessing text...")
                # 1. Preprocess
                cleaned_text = clean_text(user_input)
                
                st.write("Extracting features...")
                # 2. Vectorize
                input_vector = vectorizer.transform([cleaned_text])
                
                st.write("Running AI model prediction...")
                # 3. Predict
                prediction = model.predict(input_vector)[0]
                probabilities = model.predict_proba(input_vector)[0]
                
                # Real=0, Fake=1
                real_prob = probabilities[0]
                fake_prob = probabilities[1]
                
                # Confidence
                confidence = max(real_prob, fake_prob)
                
                if confidence < 0.60:
                    result = "UNCERTAIN"
                    color = "orange"
                elif prediction == 1:
                    result = "FAKE NEWS"
                    color = "red"
                else:
                    result = "REAL NEWS"
                    color = "green"
                
                st.write("Saving results to history...")
                # Save to database
                pred_id = insert_prediction(
                    user_input, input_method, result,
                    confidence, real_prob, fake_prob
                )
                st.session_state.current_prediction_id = pred_id
                
                st.write("Generating AI explanation (LIME)...")
                # Generate LIME explanation
                try:
                    exp_dict, features = explainer.explain_prediction(user_input, num_features=10)
                except Exception as e:
                    st.warning(f"⚠️ Could not generate explanation: {str(e)}")
                    features = []
                    exp_dict = {'prediction_class': result.replace(' NEWS', '')}
                
                status.update(label="✅ Analysis complete!", state="complete", expanded=True)

                # Display Results
                st.markdown("---")
                
                # Determine badge class
                badge_class = "fake" if result == "FAKE NEWS" else "real" if result == "REAL NEWS" else "uncertain"
                
                # Result container
                st.markdown(f"""
                <div class="result-container">
                    <p style="color: #888; font-size: 0.9rem; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.1em;">ANALYSIS RESULT</p>
                    <div class="result-badge badge-{badge_class}">{result}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Metrics Section
                st.markdown("### Confidence Metrics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Confidence", f"{confidence*100:.1f}%", 
                             help="How sure the model is about its top prediction. Above 90% is very high.")
                with col2:
                    st.metric("Real Probability", f"{real_prob*100:.1f}%",
                             help="The probability that the article features match patterns found in 'Real' news.")
                with col3:
                    st.metric("Fake Probability", f"{fake_prob*100:.1f}%",
                             help="The probability that the article features match patterns found in 'Fake' news.")
                
                # Probability visualization
                st.markdown("### Probability Distribution")
                fig = go.Figure(data=[
                    go.Bar(name='Real', x=[''], y=[real_prob*100], marker_color='#4CAF50', width=0.4),
                    go.Bar(name='Fake', x=[''], y=[fake_prob*100], marker_color='#d32f2f', width=0.4)
                ])
                fig.update_layout(
                    barmode='group',
                    yaxis_title='Percentage (%)',
                    height=250,
                    showlegend=True,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e8e8e8'),
                    xaxis=dict(showticklabels=False),
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # LIME Explanation (only if features available)
                if features:
                    st.markdown("### AI Explanation")
                    st.caption("Words that influenced the prediction (positive = supports FAKE, negative = supports REAL)")
                    
                    # Feature importance chart
                    chart_data = explainer.get_top_features_chart_data(user_input, num_features=10)
                    
                    if chart_data['words']:
                        df_features = pd.DataFrame({
                            'Word': chart_data['words'],
                            'Weight': chart_data['weights']
                        })
                        
                        # Color code based on weight
                        colors = ['#d32f2f' if w > 0 else '#4CAF50' for w in df_features['Weight']]
                        
                        fig2 = go.Figure(go.Bar(
                            x=df_features['Weight'],
                            y=df_features['Word'],
                            orientation='h',
                            marker_color=colors
                        ))
                        fig2.update_layout(
                            xaxis_title="Influence Weight",
                            height=350,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#e8e8e8'),
                            margin=dict(l=20, r=20, t=20, b=40)
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                        
                        with st.expander("View detailed weights"):
                            for word, weight in features:
                                influence = "Supports FAKE" if weight > 0 else "Supports REAL"
                                st.text(f"{word}: {weight:.4f} ({influence})")
                else:
                    st.info("AI explanation unavailable for this prediction.")
                
                # Export Options
                st.markdown("---")
                st.markdown("### Export Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # PDF Export
                    pdf_bytes = generate_pdf_report(
                        result, confidence, real_prob, fake_prob, 
                        user_input, features
                    )
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                with col2:
                    # CSV Export
                    csv_data = create_csv_export([{
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'prediction': result,
                        'confidence': confidence,
                        'real_prob': real_prob,
                        'fake_prob': fake_prob,
                        'input_method': input_method,
                        'input_text': user_input[:200] + '...' if len(user_input) > 200 else user_input
                    }])
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col3:
                    # Add to comparison
                    if st.button("Add to Compare", use_container_width=True):
                        st.session_state.comparison_articles.append({
                            'text': user_input[:500],
                            'prediction': result,
                            'confidence': confidence,
                            'real_prob': real_prob,
                            'fake_prob': fake_prob
                        })
                        st.success(f"Added ({len(st.session_state.comparison_articles)} total)")
                
                # Feedback Section
                st.markdown("---")
                st.markdown("### Feedback")
                st.caption("Was this prediction helpful?")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button("👍 Yes", use_container_width=True):
                        insert_feedback(pred_id, 'positive')
                        st.success("Thank you!")
                
                with col2:
                    if st.button("👎 No", use_container_width=True):
                        insert_feedback(pred_id, 'negative')
                        st.info("Feedback recorded")

# ==========================================
# BATCH PROCESSING MODE
# ===========================================
elif app_mode == "📦 Batch Process":
    st.header("📦 Batch Article Processing")
    st.markdown("Upload a CSV file with articles to analyze multiple items at once.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = process_batch_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} articles from CSV")
            
            st.dataframe(df.head(), use_container_width=True)
            
            if st.button("🚀 Process All Articles", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                
                for idx, row in df.iterrows():
                    status_text.text(f"Processing article {idx+1}/{len(df)}...")
                    
                    text = str(row['text'])
                    cleaned_text = clean_text(text)
                    
                    input_vector = vectorizer.transform([cleaned_text])
                    prediction = model.predict(input_vector)[0]
                    probabilities = model.predict_proba(input_vector)[0]
                    
                    real_prob = probabilities[0]
                    fake_prob = probabilities[1]
                    confidence = max(real_prob, fake_prob)
                    
                    if confidence < 0.60:
                        result = "UNCERTAIN"
                    elif prediction == 1:
                        result = "FAKE NEWS"
                    else:
                        result = "REAL NEWS"
                    
                    # Save to database
                    insert_prediction(text, 'Batch CSV', result, confidence, real_prob, fake_prob)
                    
                    results.append({
                        'text_preview': text[:100] + '...' if len(text) > 100 else text,
                        'prediction': result,
                        'confidence': f"{confidence*100:.2f}%",
                        'real_prob': f"{real_prob*100:.2f}%",
                        'fake_prob': f"{fake_prob*100:.2f}%"
                    })
                    
                    progress_bar.progress((idx + 1) / len(df))
                
                status_text.text("✅ Processing complete!")
                
                # Display results
                st.subheader("📊 Batch Results")
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True)
                
                # Summary statistics
                st.subheader("📈 Summary Statistics")
                col1, col2, col3 = st.columns(3)
                
                fake_count = len([r for r in results if r['prediction'] == 'FAKE NEWS'])
                real_count = len([r for r in results if r['prediction'] == 'REAL NEWS'])
                uncertain_count = len([r for r in results if r['prediction'] == 'UNCERTAIN'])
                
                col1.metric("Total Analyzed", len(results))
                col2.metric("Fake News", fake_count)
                col3.metric("Real News", real_count)
                
                # Pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=['Fake News', 'Real News', 'Uncertain'],
                    values=[fake_count, real_count, uncertain_count],
                    marker_colors=['red', 'green', 'orange']
                )])
                fig.update_layout(title="Prediction Distribution")
                st.plotly_chart(fig, use_container_width=True)
                
                # Export batch results
                csv_export = create_csv_export(results)
                st.download_button(
                    label="📥 Download Batch Results (CSV)",
                    data=csv_export,
                    file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("Make sure your CSV has a column named 'text', 'article', 'content', or 'headline'")

# ===========================================
# COMPARISON MODE
# ===========================================
elif app_mode == "⚖️ Compare Articles":
    st.header("⚖️ Article Comparison")
    
    if len(st.session_state.comparison_articles) == 0:
        st.info("No articles in comparison yet. Analyze articles in Single Prediction mode and add them to comparison.")
    else:
        st.success(f"Comparing {len(st.session_state.comparison_articles)} articles")
        
        # Display comparison table
        comparison_df = pd.DataFrame(st.session_state.comparison_articles)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Side by side comparison
        if len(st.session_state.comparison_articles) >= 2:
            st.subheader("📊 Visual Comparison")
            
            # Create comparison chart
            articles_data = []
            for i, article in enumerate(st.session_state.comparison_articles):
                articles_data.append({
                    'Article': f"Article {i+1}",
                    'Real %': article['real_prob'] * 100,
                    'Fake %': article['fake_prob'] * 100,
                    'Prediction': article['prediction']
                })
            
            df_comp = pd.DataFrame(articles_data)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Real %', x=df_comp['Article'], y=df_comp['Real %'], 
                                marker_color='green'))
            fig.add_trace(go.Bar(name='Fake %', x=df_comp['Article'], y=df_comp['Fake %'], 
                                marker_color='red'))
            
            fig.update_layout(barmode='group', title='Probability Comparison')
            st.plotly_chart(fig, use_container_width=True)
        
        # Clear comparison
        if st.button("🗑️ Clear Comparison"):
            st.session_state.comparison_articles = []
            st.rerun()

# ===========================================
# HISTORY MODE
# ===========================================
elif app_mode == "📜 History":
    st.header("📜 Prediction History")
    
    # Search and filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search text:")
    with col2:
        filter_type = st.selectbox("Filter by prediction:", 
                                   ["All", "REAL NEWS", "FAKE NEWS", "UNCERTAIN"])
    with col3:
        filter_method = st.selectbox("Filter by input method:", 
                                     ["All", "Paste Text", "Enter Headline", "Article URL", "Batch CSV"])
    
    # Get history
    if search_term:
        history = search_predictions(search_term, limit=100)
    else:
        pred_filter = None if filter_type == "All" else filter_type
        method_filter = None if filter_method == "All" else filter_method
        history = filter_predictions(pred_filter, method_filter, limit=100)
    
    if len(history) == 0:
        st.info("No predictions found matching your criteria.")
    else:
        st.success(f"Found {len(history)} predictions")
        
        # Convert to DataFrame for display
        df_history = pd.DataFrame(history)
        df_history['confidence'] = df_history['confidence'].apply(lambda x: f"{x*100:.2f}%")
        df_history['text_preview'] = df_history['input_text'].apply(
            lambda x: x[:100] + '...' if len(x) > 100 else x
        )
        
        display_df = df_history[['timestamp', 'prediction', 'confidence', 
                                'input_method', 'text_preview']]
        st.dataframe(display_df, use_container_width=True)
        
        # Export history
        csv_export = create_csv_export(history)
        st.download_button(
            label="📥 Download History (CSV)",
            data=csv_export,
            file_name=f"prediction_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ===========================================
# STATISTICS MODE
# ===========================================
elif app_mode == "📊 Statistics":
    st.header("📊 Statistics")
    
    stats = get_prediction_stats()
    feedback_stats = get_feedback_stats()
    
    # Simple metrics
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total", stats['total'])
    col2.metric("Fake", stats['fake_count'])
    col3.metric("Real", stats['real_count'])
    col4.metric("Confidence", f"{stats['avg_confidence']*100:.1f}%")
    
    # Prediction distribution
    if stats['total'] > 0:
        st.subheader("📈 Prediction Distribution")
        
        fig = go.Figure(data=[go.Pie(
            labels=['Fake News', 'Real News'],
            values=[stats['fake_count'], stats['real_count']],
            marker_colors=['red', 'green'],
            hole=0.3
        )])
        fig.update_layout(title="Fake vs Real Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Feedback
    st.markdown("### Feedback")
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total", feedback_stats['total'])
    col2.metric("Positive", feedback_stats['positive'] or 0)
    col3.metric("Negative", feedback_stats['negative'] or 0)
    
    if feedback_stats['total'] > 0:
        satisfaction_rate = (feedback_stats['positive'] / feedback_stats['total']) * 100
        col4.metric("Satisfaction", f"{satisfaction_rate:.1f}%")
    else:
        col4.metric("Satisfaction", "N/A")

# Footer
st.markdown("---")
with st.expander("ℹ️ About This System"):
    st.markdown("""
    ### How it works
    1. **Text Preprocessing**: Cleans and normalizes input text
    2. **Vectorization**: Converts text to numerical features using TF-IDF
    3. **Classification**: Passive Aggressive Classifier analyzes patterns
    4. **Explainability**: LIME shows which words influenced the prediction
    5. **Credibility Check**: Evaluates source domain reputation (for URLs)
    
    ### Features
    - 🔬 **AI Explainability** - Understand why predictions were made
    - 📊 **Batch Processing** - Analyze multiple articles at once
    - ⚖️ **Comparison Mode** - Compare predictions side-by-side
    - 📜 **History Tracking** - All predictions saved and searchable
    - 💾 **Export Options** - Download results as PDF or CSV
    - 🌐 **Source Credibility** - Check domain reputation
    - 🌓 **Dark Mode** - Eye-friendly interface
    - 📱 **Mobile Responsive** - Works on all devices
    
    ### Limitations
    This model detects patterns in writing style rather than fact-checking content.
    Always verify important information with trusted sources.
    """)

# Footer
st.markdown("---")
st.caption("Powered by Machine Learning")
