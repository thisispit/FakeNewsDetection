# Fake News Detection System

A professional Machine Learning powered web application that predicts whether a news article is **Real** or **Fake**, with comprehensive analytics, AI explainability, and advanced features.

## 🌟 Highlights
- **AI Explainability**: See which words influenced the prediction with LIME integration
- **Batch Processing**: Analyze hundreds of articles at once
- **Interactive Dashboards**: History tracking, statistics, and comparison tools
- **Professional UI**: Dark/Light mode with mobile-responsive design
- **Export Options**: PDF reports and CSV downloads

## 📌 Core Features

### 🔍 Prediction Engine
- **Machine Learning**: Logistic Regression with TF-IDF Vectorization
- **Confidence Score**: Probability percentage for each prediction
- **Multiple Input Methods**:
  - Full article text
  - Headlines only
  - URL (automatic text extraction)

### ✨ Advanced Features
- **AI Explainability (LIME)**: Visual word-level influence analysis
- **Source Credibility**: Domain reputation scoring for URLs
- **Prediction History**: Searchable database of all past predictions
- **Batch Analysis**: CSV upload for bulk article processing
- **Comparison Mode**: Side-by-side analysis of multiple articles
- **Interactive Charts**: Plotly visualizations for insights
- **Export Tools**: PDF reports and CSV downloads
- **User Feedback**: Rating system with analytics
- **Dark/Light Theme**: Professional UI with toggle
- **Mobile Responsive**: Touch-friendly interface

## 📂 Project Structure
```
FakeNewsDetection/
│
├── 🎯 Core Application
│   ├── app.py                  # Original simple app
│   ├── app_enhanced.py         # ⭐ Enhanced app with all features
│   ├── train_model.py          # Model training script
│   └── utils.py                # Text processing utilities
│
├── 🔧 Feature Modules
│   ├── database.py             # SQLite database operations
│   ├── explainer.py            # LIME AI explainability
│   ├── credibility.py          # Source credibility checker
│   └── export_utils.py         # PDF/CSV export tools
│
├── 📊 Data & Models
│   ├── dataset/
│   │   ├── news.csv            # Training dataset (download separately)
│   │   └── sample_data.csv     # Demo dataset included
│   ├── model/
│   │   ├── fake_news_model.pkl      # Trained model
│   │   └── tfidf_vectorizer.pkl     # TF-IDF vectorizer
│   └── data/
│       └── predictions.db      # SQLite database (auto-created)
│
├── 📖 Documentation
│   ├── README.md               # Main documentation (this file)
│   ├── QUICK_START.md          # Quick start guide
│   ├── NEW_FEATURES.md         # Detailed feature documentation
│   ├── UI_ENHANCEMENTS.md      # UI design documentation
│   └── IMPLEMENTATION_SUMMARY.md  # Development summary
│
└── ⚙️ Configuration
    ├── requirements.txt        # Python dependencies
    ├── .gitignore             # Git ignore rules
    └── download_data.py        # Dataset downloader script
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/FakeNewsDetection.git
cd FakeNewsDetection
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `streamlit` - Web framework
- `scikit-learn` - ML models
- `pandas`, `numpy` - Data processing
- `lime` - AI explainability
- `plotly` - Interactive charts
- `fpdf2` - PDF generation
- `beautifulsoup4` - URL parsing
- `requests` - HTTP requests

### 3. Prepare Dataset
The project includes `sample_data.csv` for testing. For production:

1. Download the [Fake and Real News Dataset](https://www.kaggle.com/clmentbisaillon/fake-and-real-news-dataset) from Kaggle
2. Place as `dataset/news.csv` with columns: `title`, `text`, `label`

### 4. Train the Model
```bash
python train_model.py
```
*Creates `fake_news_model.pkl` and `tfidf_vectorizer.pkl` in the `model/` directory*

### 5. Run the Application

**Option A: Enhanced Version (Recommended)**
```bash
streamlit run app_enhanced.py
```

**Option B: Simple Version**
```bash
streamlit run app.py
```

### 6. Access the App
Open your browser to `http://localhost:8501`

---

## 📱 Application Modes

The enhanced version includes 5 navigation modes:

1. **🔍 Single Prediction**
   - Analyze individual articles
   - AI explanations with LIME
   - Export to PDF/CSV
   - Source credibility checking

2. **📦 Batch Processing**
   - Upload CSV with multiple articles
   - Bulk analysis with progress tracking
   - Summary statistics and charts
   - Batch export

3. **⚖️ Comparison Mode**
   - Compare multiple articles side-by-side
   - Visual comparison charts
   - Relative probability analysis

4. **📜 History**
   - View all past predictions
   - Search and filter capabilities
   - Export history as CSV

5. **📊 Statistics**
   - Total predictions count
   - Fake vs Real distribution
   - User feedback analytics
   - Satisfaction metrics

---

## 🎓 How It Works

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

### 5. AI Explainability with LIME
**LIME (Local Interpretable Model-Agnostic Explanations)** shows which words influenced the prediction:
- Highlights important words in color (green=real, red=fake)
- Provides weight scores for each word
- Generates interactive charts
- Helps users understand the "why" behind predictions

### 6. Limitations
- The model detects **patterns in writing style** (e.g., sensationalism, specific vocabulary) rather than fact-checking content
- May incorrectly flag poorly written real news as fake
- Performance depends on training data quality
- LIME explanations take 2-3 seconds to generate
- Source credibility uses heuristics (can be enhanced with APIs)

---

## 📊 Usage Examples

### Example 1: Single Article with Explanation
```
1. Navigate to "Single Prediction"
2. Paste article text or URL
3. Click "Analyze Article"
4. View prediction with confidence score
5. Scroll to see AI explanation
6. Check influential words and charts
7. Download PDF report
```

### Example 2: Batch Processing
```
1. Prepare CSV with columns: title, text
2. Navigate to "Batch Processing"
3. Upload CSV file
4. Click "Process All Articles"
5. View results table and statistics
6. Download batch results as CSV
```

### Example 3: Compare Articles
```
1. Analyze Article A → Add to Comparison
2. Analyze Article B → Add to Comparison
3. Go to "Comparison Mode"
4. View side-by-side analysis
5. Compare probabilities and features
```

---

## 🛠️ Technologies Used

- **Python 3.x** - Core language
- **Streamlit** - Web framework
- **scikit-learn** - Machine learning
- **LIME** - AI explainability
- **Plotly** - Interactive visualizations
- **SQLite** - Database
- **FPDF2** - PDF generation
- **BeautifulSoup4** - Web scraping

---

## 📖 Documentation

- **Quick Start**: See [QUICK_START.md](QUICK_START.md)
- **Features Guide**: See [NEW_FEATURES.md](NEW_FEATURES.md)
- **UI Documentation**: See [UI_ENHANCEMENTS.md](UI_ENHANCEMENTS.md)
- **Implementation**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- Dataset: [Fake and Real News Dataset](https://www.kaggle.com/clmentbisaillon/fake-and-real-news-dataset)
- LIME Library: [LIME GitHub](https://github.com/marcotcr/lime)
- Streamlit: [Streamlit.io](https://streamlit.io)

---

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**⭐ If you find this project useful, please give it a star!**
