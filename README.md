# Fake News Detection System with Confidence Score

A Machine Learning powered web application that predicts whether a news article is **Real** or **Fake**. It provides a confidence score for each prediction and supports multiple input methods (Text, Headline, URL).

## 📌 Features
- **Machine Learning**: Uses Logistic Regression with TF-IDF Vectorization.
- **Confidence Score**: Displays the probability percentage of the prediction.
- **Multiple Inputs**:
  - Paste full text
  - Enter a headline
  - Paste a URL (Text extracted automatically)
- **User Interface**: Clean and simple UI using Streamlit.

## 📂 Project Structure
```
FakeNewsDetection/
│
├── dataset/
│   ├── news.csv           # (Download and place dataset here)
│   └── sample_data.csv    # Small demo dataset included
│
├── model/
│   ├── fake_news_model.pkl    # Trained Model (generated after training)
│   └── tfidf_vectorizer.pkl   # TF-IDF Vectorizer (generated after training)
│
├── app.py                 # Main Streamlit Application
├── train_model.py         # Script to train the ML model
├── utils.py               # Helper functions (Cleaning, URL fetching)
├── requirements.txt       # List of python dependencies
└── README.md              # Project Documentation
```

## 🚀 Setup & Installation

### 1. Install Dependencies
Make sure you have Python installed. Then run:
```bash
pip install -r requirements.txt
```

### 2. Prepare Dataset
- The project comes with a tiny `sample_data.csv` for demonstration.
- **For Real Results**: Download the "Fake News Dataset" from Kaggle (e.g., [Fake and Real News Dataset](https://www.kaggle.com/clmentbisaillon/fake-and-real-news-dataset)).
- Rename the file/merge them if necessary so you have a CSV with `title`, `text`, and `label` columns.
- Save it as `dataset/news.csv`.

### 3. Train the Model
Run the training script to build the model:
```bash
python train_model.py
```
*This will create `fake_news_model.pkl` and `tfidf_vectorizer.pkl` in the `model/` directory.*

### 4. Run the Web App
Start the Streamlit interface:
```bash
streamlit run app.py
```

---

## 🎓 Viva Explanation / How it Works

### 1. How does it work?
The system treats fake news detection as a **Binary Classification** problem.
- **Input**: News text.
- **Process**: The text is cleaned (removed punctuation, stopwords) and converted into numbers using **TF-IDF**.
- **Model**: These numbers are fed into a **Logistic Regression** model which has learned patterns from thousands of previous real/fake articles.
- **Output**: The model returns a probability (0 to 1). If > 0.5, it's classified as Fake (or Real, depending on mapping).

### 2. Why TF-IDF?
**TF-IDF (Term Frequency - Inverse Document Frequency)** counts how important a word is.
- It gives high weight to unique words that appear often in a specific article but rarely elsewhere.
- It filters out common words like "the", "is", "and" which don't help in classification.

### 3. Why Logistic Regression?
- It is simple, fast, and effective for text classification.
- Crucially, it provides a **probability score** (e.g., "80% sure this is Fake"), unlike some other algorithms (like SVM) which might just give a hard class label.

### 4. What is the Confidence Score?
The confidence score is the probability output from the model (`model.predict_proba`).
- If the model says 0.85 (85%) for "Fake", it means the features of this text strongly resemble the "Fake" examples it saw during training.

### 5. Limitations
- The model detects **patterns in writing style** (e.g., sensationalism, capital letters, specific vocabulary) rather than fact-checking the content against a knowledge base.
- It might incorrectly flag a poorly written real news article as fake.
