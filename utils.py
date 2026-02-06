import re
import string
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords

# Ensure stopwords are downloaded (handles first-time run)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def clean_text(text):
    """
    Preprocesses text data:
    1. Lowercase
    2. Remove square brackets (often used in links/citations)
    3. Remove punctuation
    4. Remove words containing numbers
    5. Remove stopwords
    """
    text = str(text).lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    
    stop_words = set(stopwords.words('english'))
    words = text.split()
    # Remove stopwords
    words = [w for w in words if w not in stop_words]
    return " ".join(words)

def fetch_text_from_url(url):
    """
    Fetches article text from a given URL using requests and BeautifulSoup.
    """
    try:
        # User-Agent header is often needed to avoid being blocked by news sites
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Attempt to find the main article text
        # This is a heuristic; different sites have different structures.
        # We look for common paragraph tags.
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])
        
        if len(text) < 50:
            return None, "Extracted text is too short. Might be protected or not an article."
            
        return text, None
    except Exception as e:
        return None, str(e)
