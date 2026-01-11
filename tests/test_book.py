import pytest
from imposition.book import Book

@pytest.fixture
def book():
    with open('test_book.epub', 'rb') as f:
        epub_bytes = f.read()
    return Book(epub_bytes)

def test_parse_toc(book):
    assert isinstance(book.toc, list)
    assert len(book.toc) > 0
    for item in book.toc:
        assert 'title' in item
        assert 'url' in item
