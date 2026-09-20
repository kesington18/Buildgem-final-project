from unittest.mock import MagicMock
from app.services.keyword_matcher import get_active_keywords, get_matched_keywords

class FakeKeyword:
    def __init__(self, term):
        self.term = term

def test_get_matched_keywords_finds_match_case_insensitive():
    keywords = [FakeKeyword("venue"), FakeKeyword("exam")]
    result = get_matched_keywords("The VENUE has changed", keywords)
    assert len(result) == 1
    assert result[0].term == "venue"

def test_get_matched_keywords_finds_multiple_matches():
    keywords = [FakeKeyword("venue"), FakeKeyword("test")]
    result = get_matched_keywords("The test venue changed", keywords)
    assert len(result) == 2

def test_get_matched_keywords_no_match_returns_empty_list():
    keywords = [FakeKeyword("venue")]
    result = get_matched_keywords("Nothing relevant here", keywords)
    assert result == []

def test_get_active_keywords_queries_with_is_active_true():
    mock_db = MagicMock()
    get_active_keywords(mock_db)
    mock_db.query.return_value.filter_by.assert_called_once_with(is_active=True)