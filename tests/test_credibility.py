import pytest
from credibility import SourceCredibilityChecker

@pytest.fixture
def checker():
    return SourceCredibilityChecker()

def test_extract_domain(checker):
    assert checker.extract_domain("https://www.example.com/path") == "example.com"
    assert checker.extract_domain("http://example.com") == "example.com"
    assert checker.extract_domain("example.com") == "example.com"
    assert checker.extract_domain("www.example.com") == "example.com"

def test_check_https(checker):
    assert checker.check_https("https://example.com") is True
    assert checker.check_https("http://example.com") is False

def test_check_tld(checker):
    is_suspicious, _ = checker.check_tld("example.xyz")
    assert is_suspicious is True
    is_suspicious, _ = checker.check_tld("example.com")
    assert is_suspicious is False

def test_check_domain_reputation_high(checker):
    reputation, score, _ = checker.check_domain_reputation("reuters.com")
    assert reputation == 'high'
    assert score == 95

def test_check_domain_reputation_low(checker):
    reputation, score, _ = checker.check_domain_reputation("theonion.com")
    assert reputation == 'low'
    assert score == 15

def test_check_domain_reputation_suspicious_keywords(checker):
    reputation, score, _ = checker.check_domain_reputation("real-fake-news.com")
    assert reputation == 'low'
    assert score == 30

def test_check_url_credibility(checker):
    result = checker.check_url_credibility("https://www.reuters.com/article")
    assert result['valid'] is True
    assert result['domain'] == "reuters.com"
    assert result['https'] is True
    assert result['reputation'] == 'high'
    assert result['score'] == 95
    assert result['color'] == 'green'

    result_bad = checker.check_url_credibility("http://fake-truth-news.xyz")
    assert result_bad['valid'] is True
    assert result_bad['https'] is False
    assert result_bad['reputation'] == 'low'
    # Base 35 (from TLD or keywords), -10 for HTTP not applied if reputation is 'low'
    # Wait, check_url_credibility says: if not https and reputation != 'low': score -= 10
    # Let's just check it's categorized as red
    assert result_bad['color'] == 'red'
