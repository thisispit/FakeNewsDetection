import pandas as pd
from fpdf import FPDF
from datetime import datetime
from typing import List, Dict, Optional
import io

class PDFReport(FPDF):
    """Custom PDF report for fake news detection results."""
    
    def header(self):
        """Page header."""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Fake News Detection Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        """Page footer."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def add_metadata(self, timestamp: str):
        """Add report metadata."""
        self.set_font('Arial', '', 10)
        self.cell(0, 8, f'Generated: {timestamp}', 0, 1)
        self.ln(5)
    
    def add_prediction_result(self, prediction: str, confidence: float, 
                            real_prob: float, fake_prob: float):
        """Add prediction results section."""
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Prediction Result', 0, 1)
        
        self.set_font('Arial', 'B', 12)
        
        # Set color based on prediction
        if prediction == 'FAKE NEWS':
            self.set_text_color(255, 0, 0)
        elif prediction == 'REAL NEWS':
            self.set_text_color(0, 128, 0)
        else:
            self.set_text_color(255, 165, 0)
        
        self.cell(0, 10, f'Result: {prediction}', 0, 1)
        self.set_text_color(0, 0, 0)
        
        self.set_font('Arial', '', 11)
        self.cell(0, 8, f'Confidence: {confidence*100:.2f}%', 0, 1)
        self.cell(0, 8, f'Real Probability: {real_prob*100:.2f}%', 0, 1)
        self.cell(0, 8, f'Fake Probability: {fake_prob*100:.2f}%', 0, 1)
        self.ln(5)
    
    def add_text_sample(self, text: str, max_length: int = 500):
        """Add analyzed text sample."""
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Analyzed Text Sample', 0, 1)
        
        self.set_font('Arial', '', 10)
        
        # Truncate if too long
        display_text = text[:max_length]
        if len(text) > max_length:
            display_text += '...'
        
        # Multi-cell for word wrapping
        self.multi_cell(0, 6, display_text)
        self.ln(5)
    
    def add_explanation(self, features: List[tuple], prediction_class: str):
        """Add LIME explanation if available."""
        if not features:
            return
        
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Top Influential Words', 0, 1)
        
        self.set_font('Arial', '', 10)
        self.cell(60, 8, 'Word/Phrase', 1, 0, 'C')
        self.cell(40, 8, 'Weight', 1, 0, 'C')
        self.cell(80, 8, 'Influence', 1, 1, 'C')
        
        for word, weight in features[:10]:
            self.cell(60, 8, word[:30], 1, 0)
            self.cell(40, 8, f'{weight:.4f}', 1, 0, 'C')
            
            if weight > 0:
                influence = f'Supports {prediction_class}'
            else:
                influence = f'Opposes {prediction_class}'
            
            self.cell(80, 8, influence, 1, 1)
        
        self.ln(5)

def generate_pdf_report(prediction: str, confidence: float, real_prob: float, 
                       fake_prob: float, text: str, features: Optional[List[tuple]] = None) -> bytes:
    """
    Generate a PDF report for a single prediction.
    
    Args:
        prediction: Prediction result (REAL NEWS/FAKE NEWS)
        confidence: Confidence score
        real_prob: Real news probability
        fake_prob: Fake news probability
        text: Input text
        features: Optional LIME features
    
    Returns:
        PDF bytes
    """
    pdf = PDFReport()
    pdf.add_page()
    
    # Add metadata
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pdf.add_metadata(timestamp)
    
    # Add prediction results
    pdf.add_prediction_result(prediction, confidence, real_prob, fake_prob)
    
    # Add text sample
    pdf.add_text_sample(text)
    
    # Add explanation if available
    if features:
        prediction_class = prediction.replace(' NEWS', '')
        pdf.add_explanation(features, prediction_class)
    
    # Get PDF bytes - fpdf2 returns bytearray, convert to bytes
    pdf_output = pdf.output()
    return bytes(pdf_output)

def create_csv_export(predictions: List[Dict]) -> str:
    """
    Create CSV export from predictions list.
    
    Args:
        predictions: List of prediction dictionaries
    
    Returns:
        CSV string
    """
    if not predictions:
        return ""
    
    df = pd.DataFrame(predictions)
    
    # Select and order columns
    columns = ['timestamp', 'prediction', 'confidence', 'real_prob', 'fake_prob', 
               'input_method', 'input_text']
    
    # Only include columns that exist
    available_columns = [col for col in columns if col in df.columns]
    df = df[available_columns]
    
    # Format percentages
    if 'confidence' in df.columns:
        df['confidence'] = df['confidence'].apply(lambda x: f'{x*100:.2f}%')
    if 'real_prob' in df.columns:
        df['real_prob'] = df['real_prob'].apply(lambda x: f'{x*100:.2f}%')
    if 'fake_prob' in df.columns:
        df['fake_prob'] = df['fake_prob'].apply(lambda x: f'{x*100:.2f}%')
    
    # Convert to CSV
    return df.to_csv(index=False)

def process_batch_csv(uploaded_file) -> pd.DataFrame:
    """
    Process uploaded CSV file for batch predictions.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        DataFrame with text column
    """
    try:
        df = pd.read_csv(uploaded_file)
        
        # Check for required column (text, article, content, headline, etc.)
        text_columns = ['text', 'article', 'content', 'headline', 'title', 'body']
        
        found_column = None
        for col in text_columns:
            if col in df.columns:
                found_column = col
                break
        
        if found_column:
            # Rename to 'text' for consistency
            df['text'] = df[found_column]
        else:
            # If no standard column found, use first column
            if len(df.columns) > 0:
                df['text'] = df[df.columns[0]]
            else:
                raise ValueError("No valid text column found in CSV")
        
        # Remove empty rows
        df = df[df['text'].notna()]
        df = df[df['text'].str.strip() != '']
        
        return df
        
    except Exception as e:
        raise ValueError(f"Error processing CSV: {str(e)}")
