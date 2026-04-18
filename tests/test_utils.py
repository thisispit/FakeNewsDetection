import pytest
from utils import clean_text

def test_clean_text_lowercase():
    assert clean_text("HELLO World") == "hello world"

def test_clean_text_remove_punctuation():
    assert clean_text("Hello, world! This is a test.") == "hello world test"

def test_clean_text_remove_brackets():
    assert clean_text("Hello [world] this is [a] test") == "hello test"

def test_clean_text_remove_numbers():
    assert clean_text("There are 100 apples and 5 oranges") == "apples oranges"

def test_clean_text_remove_stopwords():
    # 'this', 'is', 'a' are typical stopwords
    assert clean_text("This is a simple test") == "simple test"

def test_clean_text_combined():
    text = "The QUICK brown fox [jumps] over 13 lazy dogs!!"
    expected = "quick brown fox lazy dogs"
    assert clean_text(text) == expected
