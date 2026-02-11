import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, classification_report
from utils import clean_text

# Paths
DATASET_DIR = 'dataset'
MODEL_PATH = 'model/fake_news_model.pkl'
VECTORIZER_PATH = 'model/tfidf_vectorizer.pkl'

def load_data():
    """
    Robust data loader that tries to find:
    1. ISOT dataset (Fake.csv, True.csv)
    2. DataCamp dataset (fake_or_real_news.csv)
    3. Politifact dataset (news.csv)
    4. Sample data (sample_data.csv)
    """
    # 1. Check for ISOT
    fake_path = os.path.join(DATASET_DIR, 'Fake.csv')
    true_path = os.path.join(DATASET_DIR, 'True.csv')
    
    if os.path.exists(fake_path) and os.path.exists(true_path):
        print("Loading ISOT dataset (Fake.csv/True.csv)...")
        try:
            df_fake = pd.read_csv(fake_path)
            df_true = pd.read_csv(true_path)
            
            # Add labels
            df_fake['label'] = 'FAKE'
            df_true['label'] = 'REAL'
            
            # ISOT usually has 'title', 'text', 'subject', 'date'.
            # We combine title and text for better context.
            # Handle potential missing columns if file format differs
            if 'text' not in df_fake.columns: df_fake['text'] = ""
            if 'title' not in df_fake.columns: df_fake['title'] = ""
            if 'text' not in df_true.columns: df_true['text'] = ""
            if 'title' not in df_true.columns: df_true['title'] = ""

            df = pd.concat([df_fake, df_true], ignore_index=True)
            df['text'] = df['title'] + " " + df['text']
            return df
        except Exception as e:
            print(f"Error loading ISOT: {e}")

    # 2. Check for DataCamp
    csv_path = os.path.join(DATASET_DIR, 'fake_or_real_news.csv')
    if os.path.exists(csv_path):
        print("Loading DataCamp dataset...")
        return pd.read_csv(csv_path)

    # 3. Check for Politifact (news.csv)
    news_path = os.path.join(DATASET_DIR, 'news.csv')
    if os.path.exists(news_path):
        print("Loading Politifact dataset (news.csv)...")
        return pd.read_csv(news_path)

    # 4. Fallback
    sample_path = os.path.join(DATASET_DIR, 'sample_data.csv')
    if os.path.exists(sample_path):
        print("Loading Sample dataset...")
        return pd.read_csv(sample_path)

    raise FileNotFoundError("No valid dataset found in 'dataset/'. Please run download_data.py or add Fake.csv/True.csv.")

def train():
    df = load_data()
    
    # Ensure text column exists
    if 'text' not in df.columns and 'title' in df.columns:
        print("Warning: 'text' column missing. Using 'title' as text.")
        df['text'] = df['title']
    
    # Drop rows with no text
    df = df.dropna(subset=['text'])
    
    print(f"Dataset size: {len(df)} rows")
    print("Cleaning text data (this may take a while)...")
    df['clean_text'] = df['text'].apply(clean_text)
    
    # Label Encoding
    # Normalize labels
    df['label'] = df['label'].astype(str).str.upper()
    mapping = {'FAKE': 1, 'REAL': 0, 'TRUE': 0, 'FALSE': 1}
    
    # Filter only known labels
    df = df[df['label'].isin(mapping.keys())]
    df['label_num'] = df['label'].map(mapping)

    print("Vectorizing text (TF-IDF with N-grams)...")
    # max_features limits the size to prevent memory errors
    vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7, ngram_range=(1,2), max_features=50000) 
    X = vectorizer.fit_transform(df['clean_text'])
    y = df['label_num']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Passive Aggressive Classifier with Calibration...")
    
    # We use a base PAC
    base_model = PassiveAggressiveClassifier(max_iter=50, random_state=42)
    
    # Calibrated for probabilities
    model = CalibratedClassifierCV(base_model, method='sigmoid', cv=3)
    model.fit(X_train, y_train)
    
    print("Evaluating Model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy*100:.2f}%")
    
    try:
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['REAL', 'FAKE']))
    except:
        pass
    
    # Ensure model directory exists
    if not os.path.exists('model'):
        os.makedirs('model')

    print("Saving model and vectorizer...")
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print("Saved successfully.")

if __name__ == "__main__":
    train()