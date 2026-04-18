# Copilot Instructions for `FakeNewsDetection`

## Build, run, and test commands

```bash
pip install -r requirements.txt
python train_model.py
streamlit run app_enhanced.py
```

Run tests from repository root (PowerShell):

```powershell
$env:PYTHONPATH='.'; pytest -q
```

Run a single test:

```powershell
$env:PYTHONPATH='.'; pytest -q tests/test_utils.py::test_clean_text_combined
```

There is no dedicated lint configuration (no `ruff`, `flake8`, `pylint`, or `mypy` config files in this repo).

## High-level architecture

- `train_model.py` is the training pipeline. It tries multiple dataset formats under `dataset\` (ISOT `Fake.csv`/`True.csv`, DataCamp `fake_or_real_news.csv`, Politifact-style `news.csv`, then `sample_data.csv` fallback), normalizes labels, applies `utils.clean_text`, trains a calibrated Passive-Aggressive model on TF-IDF features, and saves artifacts to:
  - `model\fake_news_model.pkl`
  - `model\tfidf_vectorizer.pkl`
- `app_enhanced.py` is the main app entrypoint. On startup it:
  - initializes SQLite via `database.init_database()`
  - loads model/vectorizer artifacts
  - creates a `FakeNewsExplainer` (`explainer.py`) for LIME explanations
  - routes UI into 5 modes: Analyze Article, Batch Process, Compare Articles, History, Statistics.
- Inference flow (single and batch): input -> `utils.clean_text` -> vectorizer transform -> model predict + predict_proba -> label mapping/display -> persistence in SQLite.
- `database.py` stores predictions and feedback in `data\predictions.db` and powers History/Statistics screens.
- `credibility.py` adds URL/domain credibility heuristics used when the user submits article URLs.
- `export_utils.py` handles report exports:
  - PDF (`fpdf2`) for single prediction reports
  - CSV exports for single, history, and batch results.

## Key codebase conventions

- Keep preprocessing centralized in `utils.clean_text`. Training and inference both depend on this exact function; avoid introducing alternative cleaning paths.
- Prediction labels are string-based and used across UI, DB, filters, and stats:
  - `REAL NEWS`
  - `FAKE NEWS`
  - `UNCERTAIN`
- `UNCERTAIN` is determined by a confidence threshold of `0.60` (`max(real_prob, fake_prob) < 0.60`) in both single and batch flows.
- Model artifact paths are hard-coded in apps/training (`model/fake_news_model.pkl`, `model/tfidf_vectorizer.pkl`); keep these stable unless updating all call sites.
- Database records intentionally truncate stored `input_text` to 5000 chars in `insert_prediction`; preserve this behavior when changing persistence logic.
- Batch CSV ingestion expects one text-like column and normalizes to `text` (`text`, `article`, `content`, `headline`, `title`, `body`, else first column).
