import requests
from urllib.parse import urlparse
from typing import Tuple, Optional
import re

class SourceCredibilityChecker:
    """Check source credibility using multiple heuristics and APIs."""
    
    # Known credible domains (can be expanded)
    CREDIBLE_DOMAINS = {
        'reuters.com', 'apnews.com', 'bbc.com', 'bbc.co.uk', 'npr.org',
        'wsj.com', 'nytimes.com', 'washingtonpost.com', 'theguardian.com',
        'cnn.com', 'cnbc.com', 'bloomberg.com', 'economist.com', 'forbes.com',
        'ft.com', 'usatoday.com', 'abcnews.go.com', 'cbsnews.com', 'nbcnews.com',
        'time.com', 'newsweek.com', 'politico.com', 'thehill.com'
    }
    
    # Known unreliable/satirical domains
    UNRELIABLE_DOMAINS = {
        'theonion.com', 'clickhole.com', 'reductress.com',
        'beforeitsnews.com', 'naturalnews.com', 'infowars.com'
    }
    
    # Suspicious TLDs
    SUSPICIOUS_TLDS = {'.xyz', '.club', '.top', '.online', '.site', '.bid', '.info'}
    
    def __init__(self):
        """Initialize the credibility checker."""
        pass
    
    def extract_domain(self, url: str) -> Optional[str]:
        """
        Extract domain from URL.
        
        Args:
            url: Full URL string
            
        Returns:
            Domain string or None if invalid
        """
        try:
            # Add scheme if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain if domain else None
        except Exception:
            return None
    
    def check_https(self, url: str) -> bool:
        """Check if URL uses HTTPS."""
        return url.startswith('https://')
    
    def check_tld(self, domain: str) -> Tuple[bool, str]:
        """
        Check if domain has suspicious TLD.
        
        Returns:
            Tuple of (is_suspicious, reason)
        """
        for tld in self.SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                return True, f"Suspicious TLD: {tld}"
        return False, "TLD appears normal"
    
    def check_domain_reputation(self, domain: str) -> Tuple[str, int, str]:
        """
        Check domain reputation using heuristics.
        
        Returns:
            Tuple of (reputation, score, details)
            - reputation: 'high', 'medium', 'low', 'unknown'
            - score: 0-100
            - details: Explanation string
        """
        if domain in self.CREDIBLE_DOMAINS:
            return 'high', 95, f"Known credible source: {domain}"
        
        if domain in self.UNRELIABLE_DOMAINS:
            return 'low', 15, f"Known unreliable/satirical source: {domain}"
        
        # Check for suspicious patterns
        suspicious_keywords = ['fake', 'hoax', 'conspiracy', 'truth', 'real', 'news']
        domain_parts = domain.replace('.', ' ').replace('-', ' ').split()
        
        keyword_count = sum(1 for kw in suspicious_keywords if kw in domain_parts)
        
        if keyword_count >= 2:
            return 'low', 30, f"Domain name contains suspicious keywords"
        
        # Check TLD
        is_suspicious, tld_reason = self.check_tld(domain)
        if is_suspicious:
            return 'low', 35, tld_reason
        
        # Unknown domain - medium credibility
        return 'medium', 50, "Unknown domain - no reputation data available"
    
    def check_url_credibility(self, url: str) -> dict:
        """
        Comprehensive credibility check for a URL.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with credibility information
        """
        domain = self.extract_domain(url)
        
        if not domain:
            return {
                'valid': False,
                'domain': None,
                'https': False,
                'reputation': 'unknown',
                'score': 0,
                'details': 'Invalid URL format',
                'color': 'gray'
            }
        
        https = self.check_https(url)
        reputation, score, details = self.check_domain_reputation(domain)
        
        # Adjust score based on HTTPS
        if not https and reputation != 'low':
            score -= 10
            details += " | No HTTPS encryption"
        
        # Determine color for UI
        if score >= 70:
            color = 'green'
        elif score >= 40:
            color = 'orange'
        else:
            color = 'red'
        
        return {
            'valid': True,
            'domain': domain,
            'https': https,
            'reputation': reputation,
            'score': score,
            'details': details,
            'color': color
        }

def check_source_credibility(url: str) -> dict:
    """
    Convenience function to check source credibility.
    
    Args:
        url: URL to check
        
    Returns:
        Credibility information dictionary
    """
    checker = SourceCredibilityChecker()
    return checker.check_url_credibility(url)
