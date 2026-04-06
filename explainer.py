import numpy as np
from lime.lime_text import LimeTextExplainer
from typing import Tuple, List, Dict

class FakeNewsExplainer:
    """Wrapper for LIME explainability for fake news detection."""
    
    def __init__(self, model, vectorizer, class_names=['REAL', 'FAKE']):
        """
        Initialize the explainer.
        
        Args:
            model: Trained classification model with predict_proba method
            vectorizer: Fitted TF-IDF vectorizer
            class_names: List of class names
        """
        self.model = model
        self.vectorizer = vectorizer
        self.class_names = class_names
        self.explainer = LimeTextExplainer(class_names=class_names)
    
    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """
        Prediction function for LIME.
        
        Args:
            texts: List of text strings
            
        Returns:
            Probability array of shape (n_samples, n_classes)
        """
        # Transform texts using vectorizer
        vectors = self.vectorizer.transform(texts)
        # Get probabilities from model
        probabilities = self.model.predict_proba(vectors)
        return probabilities
    
    def explain_prediction(self, text: str, num_features: int = 10) -> Tuple[Dict, List[Tuple[str, float]]]:
        """
        Generate explanation for a prediction.
        
        Args:
            text: Input text to explain
            num_features: Number of top features to show
            
        Returns:
            Tuple of (explanation_dict, top_features_list)
            - explanation_dict: Full LIME explanation object data
            - top_features_list: List of (word, weight) tuples
        """
        # Get prediction first
        vector = self.vectorizer.transform([text])
        proba = self.model.predict_proba(vector)[0]
        prediction_class = 1 if proba[1] > proba[0] else 0
        
        try:
            # Generate explanation
            exp = self.explainer.explain_instance(
                text, 
                self.predict_proba, 
                num_features=num_features,
                num_samples=1000,
                labels=(prediction_class,)  # Specify which class to explain
            )
            
            # Extract feature weights for the predicted class
            features = exp.as_list(label=prediction_class)
            
            # Create explanation dictionary
            explanation_dict = {
                'prediction_class': self.class_names[prediction_class],
                'prediction_proba': proba,
                'features': features,
                'intercept': exp.intercept[prediction_class] if hasattr(exp, 'intercept') else 0,
                'score': exp.score if hasattr(exp, 'score') else None
            }
            
            return explanation_dict, features
        
        except Exception as e:
            # Fallback: return empty features if LIME fails
            explanation_dict = {
                'prediction_class': self.class_names[prediction_class],
                'prediction_proba': proba,
                'features': [],
                'intercept': 0,
                'score': None,
                'error': str(e)
            }
            return explanation_dict, []
    
    def get_word_importance_html(self, text: str, num_features: int = 15) -> str:
        """
        Generate HTML with color-coded word importance.
        
        Args:
            text: Input text
            num_features: Number of features to highlight
            
        Returns:
            HTML string with highlighted words
        """
        exp_dict, features = self.explain_prediction(text, num_features)
        
        # Create a dictionary of word -> weight
        word_weights = {}
        for word, weight in features:
            # LIME returns phrases sometimes, we'll handle the base word
            clean_word = word.strip().lower()
            word_weights[clean_word] = weight
        
        # Split text into words
        words = text.split()
        html_parts = []
        
        for word in words:
            clean_word = word.strip().lower()
            
            # Check if this word (or a version of it) is in our important features
            weight = word_weights.get(clean_word, 0)
            
            if abs(weight) > 0.01:  # Only highlight significant words
                # Positive weight = supports FAKE (red)
                # Negative weight = supports REAL (green)
                if weight > 0:
                    # Red for fake indicators
                    intensity = min(int(abs(weight) * 200), 200)
                    html_parts.append(
                        f'<span style="background-color: rgba(255, 0, 0, {intensity/255:.2f}); '
                        f'padding: 2px 4px; border-radius: 3px; margin: 0 2px;" '
                        f'title="Fake indicator: {weight:.3f}">{word}</span>'
                    )
                else:
                    # Green for real indicators
                    intensity = min(int(abs(weight) * 200), 200)
                    html_parts.append(
                        f'<span style="background-color: rgba(0, 255, 0, {intensity/255:.2f}); '
                        f'padding: 2px 4px; border-radius: 3px; margin: 0 2px;" '
                        f'title="Real indicator: {weight:.3f}">{word}</span>'
                    )
            else:
                html_parts.append(word)
        
        return ' '.join(html_parts)
    
    def get_top_features_chart_data(self, text: str, num_features: int = 10) -> Dict:
        """
        Get data formatted for plotting feature importance.
        
        Args:
            text: Input text
            num_features: Number of top features
            
        Returns:
            Dictionary with 'words' and 'weights' lists
        """
        exp_dict, features = self.explain_prediction(text, num_features)
        
        if not features:
            # Return empty data if no features
            return {
                'words': [],
                'weights': [],
                'prediction': exp_dict['prediction_class']
            }
        
        # Sort by absolute weight for better visualization
        sorted_features = sorted(features, key=lambda x: abs(x[1]), reverse=True)
        
        words = [f[0] for f in sorted_features]
        weights = [f[1] for f in sorted_features]
        
        return {
            'words': words,
            'weights': weights,
            'prediction': exp_dict['prediction_class']
        }
