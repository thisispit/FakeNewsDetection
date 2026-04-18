# Fake News Detection System

A professional Machine Learning powered web application that predicts whether a news article is **Real** or **Fake**, with comprehensive analytics, AI explainability, and advanced features.

## 🌟 Highlights
- **AI Explainability**: See which words influenced the prediction with LIME integration
- **Batch Processing**: Analyze hundreds of articles at once
- **Interactive Dashboards**: History tracking, statistics, and comparison tools
- **Professional UI**: Dark theme with mobile-responsive design and granular loading states
- **Export Options**: PDF reports and CSV downloads

## 📌 Core Features

### 🔍 Prediction Engine
- **Machine Learning**: Passive Aggressive Classifier with TF-IDF Vectorization
- **Confidence Score**: Probability percentage with interactive tooltips
- **Multiple Input Methods**:
  - Full article text
  - Headlines only
  - URL (with robust validation and automatic text extraction)

### ✨ Advanced Features
- **AI Explainability (LIME)**: Visual word-level influence analysis
- **Source Credibility**: Domain reputation scoring for URLs with security checks
- **Prediction History**: Searchable SQLite database of all past predictions
- **Batch Analysis**: CSV upload for bulk article processing with progress tracking
- **Comparison Mode**: Side-by-side analysis of multiple articles
- **Interactive Charts**: Plotly visualizations for insights
- **Export Tools**: PDF reports and CSV downloads
- **User Feedback**: Rating system with analytics

## 📂 Project Structure
```
FakeNewsDetection/
│
├── 🎯 Core Application
│   ├── app.py                  # Main Streamlit application
│   ├── train_model.py          # Model training script
│   └── utils.py                # Text processing & URL validation utilities
│
├── 🔧 Feature Modules
│   ├── database.py             # SQLite database operations
│   ├── explainer.py            # LIME AI explainability
│   ├── credibility.py          # Source credibility checker
│   └── export_utils.py         # PDF/CSV export tools
│
├── 📊 Data & Models
│   ├── dataset/
│   │   ├── news.csv            # Training dataset
│   │   └── sample_data.csv     # Demo dataset
│   ├── model/
│   │   ├── fake_news_model.pkl      # Trained model
│   │   └── tfidf_vectorizer.pkl     # TF-IDF vectorizer
│   └── data/
│       └── predictions.db      # SQLite database (auto-created)
│
├── 📖 Documentation
│   ├── README.md               # Main documentation
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
```
```bash
cd FakeNewsDetection
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Prepare Dataset
The project includes `sample_data.csv` for testing. To train on a full dataset:
1. Run `python download_data.py` to fetch Politifact data.
2. OR place your own `news.csv` in the `dataset/` folder.

### 4. Train the Model
```bash
python train_model.py
```
*Creates the model and vectorizer in the `model/` directory.*

### 5. Run the Application
```bash
streamlit run app.py
```

### 6. Access the App
Open your browser to `http://localhost:8501`

---

## 📱 Application Modes

1. **🔍 Single Prediction**
   - Analyze individual articles with granular loading states
   - AI explanations with LIME highlighting
   - URL validation and content-type checking
   - Export to PDF/CSV

2. **📦 Batch Processing**
   - Upload CSV with multiple articles
   - Bulk analysis with progress tracking
   - Summary statistics and charts

3. **⚖️ Comparison Mode**
   - Compare multiple articles side-by-side
   - Visual probability distribution charts

4. **📜 History**
   - View all past predictions with search and filter
   - Export history as CSV

5. **📊 Statistics**
   - Total predictions and class distribution
   - User feedback analytics

---

## 🎓 How It Works

### 1. The Model
The system uses a **Passive Aggressive Classifier** calibrated for probability outputs. It is particularly well-suited for large-scale text classification.

### 2. TF-IDF Vectorization
Text is converted into numerical features using **TF-IDF (Term Frequency - Inverse Document Frequency)** with N-grams (1,2), capturing both individual words and common phrases.

### 3. AI Explainability
Using **LIME**, the system perturbs the input text to see which words most influence the model's decision, highlighting them in the UI (Red for Fake indicators, Green for Real).

### 4. URL Validation & Credibility
The system performs a HEAD request to verify content types (preventing non-HTML downloads) and evaluates domain reputation based on a curated list of credible and unreliable sources.

---

## 🛠️ Technologies Used

- **Python 3.x**
- **Streamlit** (Web UI)
- **Scikit-learn** (Machine Learning)
- **LIME** (AI Explainability)
- **Plotly** (Visualizations)
- **SQLite** (Data Persistence)
- **FPDF2** (PDF Generation)
- **BeautifulSoup4** (Web Scraping)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

**⭐ If you find this project useful, please give it a star!**
