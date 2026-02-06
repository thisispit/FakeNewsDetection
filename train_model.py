import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from utils import clean_text

# Paths
DATASET_PATH = 'dataset/news.csv'
SAMPLE_DATA_PATH = 'dataset/sample_data.csv'
MODEL_PATH = 'model/fake_news_model.pkl'
VECTORIZER_PATH = 'model/tfidf_vectorizer.pkl'

def load_data():
    """Loads dataset. Prioritizes 'news.csv', falls back to 'sample_data.csv'."""
    if os.path.exists(DATASET_PATH):
        print(f"Loading main dataset from {DATASET_PATH}...")
        df = pd.read_csv(DATASET_PATH)
    elif os.path.exists(SAMPLE_DATA_PATH):
        print(f"Main dataset not found. Loading sample dataset from {SAMPLE_DATA_PATH}...")
        df = pd.read_csv(SAMPLE_DATA_PATH)
    else:
        raise FileNotFoundError("No dataset found in 'dataset/' directory.")
    return df

def train():
    df = load_data()
    df = df.dropna(subset=['text'])
    
    print("Cleaning text data...")
    df['clean_text'] = df['text'].apply(clean_text)
    
    # Label Encoding
    if df['label'].dtype == 'object':
        mapping = {'FAKE': 1, 'REAL': 0, 'Fake': 1, 'Real': 0, 'fake': 1, 'real': 0, 'TRUE': 0, 'FALSE': 1, 'true': 0, 'false': 1}
        df['label_num'] = df['label'].map(mapping)
        df = df.dropna(subset=['label_num'])
    else:
        df['label_num'] = df['label']

    print("Vectorizing text (TF-IDF with N-grams)...")
    vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7, ngram_range=(1,2)) 
    X = vectorizer.fit_transform(df['clean_text'])
    y = df['label_num']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Passive Aggressive Classifier with Calibration...")
    # CalibratedClassifierCV allows us to get probabilities (predict_proba) from PassiveAggressive
    base_model = PassiveAggressiveClassifier(max_iter=50)
    model = CalibratedClassifierCV(base_model, method='sigmoid', cv=3)
    model.fit(X_train, y_train)
    
    print("Evaluating Model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {accuracy*100:.2f}%")
    
    print("Saving model and vectorizer...")
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print("Saved successfully.")

if __name__ == "__main__":
    train()
