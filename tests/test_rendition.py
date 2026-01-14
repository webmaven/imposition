import sys
from unittest.mock import MagicMock, patch, call
import xml.etree.ElementTree as ET

import pytest

# Mock the 'js' and 'pyodide' modules before importing the code that uses them
sys.modules["js"] = MagicMock()
sys.modules["pyodide"] = MagicMock()
sys.modules["pyodide.ffi"] = MagicMock()


# Since we've mocked the js module, we can now import the Rendition class
from imposition.rendition import Rendition  # noqa: E402
from imposition.book import Book # noqa: E402


@pytest.fixture
def mock_book():
    """Fixture to create a mock Book object."""
    book = MagicMock(spec=Book)
    book.toc = [
        {"title": "Chapter 1", "url": "OEBPS/chapter1.xhtml"},
        {"title": "Chapter 2", "url": "OEBPS/chapter2.xhtml"},
    ]
    book.spine = ["OEBPS/chapter1.xhtml", "OEBPS/chapter2.xhtml"]
    book.zip_file = MagicMock()
    # Mock the read method to return some basic HTML content
    book.zip_file.read.return_value = b'<html><head></head><body><p>Test</p></body></html>'
    return book


@pytest.fixture
def mock_document():
    """Fixture to create a mock of the global `document` object."""
    target_element = MagicMock(name="target_element")
    toc_container = MagicMock(name="toc_container")
    iframe = MagicMock(name="iframe")
    ul = MagicMock(name="ul")

    document_mock = MagicMock(name="document")

    def get_element_by_id(id_):
        if id_ == "viewer":
            return target_element
        if id_ == "toc-container":
            return toc_container
        return MagicMock()
    document_mock.getElementById.side_effect = get_element_by_id

    def create_element(tag):
        # Access call_count from the mock, not the function itself
        call_count = document_mock.createElement.call_count
        if tag == 'iframe':
            return iframe
        if tag == 'ul':
            return ul
        # Return a new mock for other elements to avoid side effects
        element_mock = MagicMock(name=f"{tag}_{call_count}")
        element_mock.appendChild.return_value = element_mock
        return element_mock
    document_mock.createElement.side_effect = create_element

    return document_mock

def test_rendition_initialization(mock_book, mock_document):
    """Test that the Rendition class initializes correctly."""
    with patch("imposition.rendition.document", mock_document):
        rendition = Rendition(mock_book, "viewer")
        assert rendition.book is mock_book
        assert rendition.target_id == "viewer"
        mock_document.getElementById.assert_called_with("viewer")
        assert rendition.target_element is not None
        assert rendition.iframe is not None

def test_display_toc(mock_book, mock_document):
    """Test that the display_toc method correctly generates the TOC."""
    with patch("imposition.rendition.document", mock_document):
        rendition = Rendition(mock_book, "viewer")
        rendition.display_toc()

        toc_container = mock_document.getElementById("toc-container")
        ul_element = mock_document.createElement('ul')

        # Check that the container was cleared and the final UL was appended
        assert toc_container.innerHTML == ''
        toc_container.appendChild.assert_called_once_with(ul_element)

def test_display_first_chapter(mock_book, mock_document):
    """Test displaying the first chapter by default."""
    with patch("imposition.rendition.document", mock_document):
        rendition = Rendition(mock_book, "viewer")
        rendition.display()
        mock_book.zip_file.read.assert_called_once_with(mock_book.spine[0])
        assert "data:text/html;base64," in rendition.iframe.src

def test_display_specific_chapter(mock_book, mock_document):
    """Test displaying a specific chapter by URL."""
    with patch("imposition.rendition.document", mock_document):
        rendition = Rendition(mock_book, "viewer")
        chapter_url = "OEBPS/chapter2.xhtml"
        rendition.display(chapter_url)
        mock_book.zip_file.read.assert_called_once_with(chapter_url)
        assert "data:text/html;base64," in rendition.iframe.src

def test_display_with_anchor(mock_book, mock_document):
    """Test that displaying a chapter with an anchor sets the iframe onload property."""
    with patch("imposition.rendition.document", mock_document):
        rendition = Rendition(mock_book, "viewer")
        chapter_url = "OEBPS/chapter1.xhtml#section1"
        rendition.display(chapter_url)
        assert rendition.iframe.onload == "this.contentWindow.location.hash = '#section1'"

def test_next_chapter(mock_book, mock_document):
    """Test navigating to the next chapter."""
    with patch("imposition.rendition.document", mock_document) as mock_doc:
        rendition = Rendition(mock_book, "viewer")
        rendition.current_chapter_index = 0
        with patch.object(rendition, 'display') as mock_display:
            rendition.next_chapter()
            assert rendition.current_chapter_index == 1
            mock_display.assert_called_once_with(mock_book.spine[1])

def test_previous_chapter(mock_book, mock_document):
    """Test navigating to the previous chapter."""
    with patch("imposition.rendition.document", mock_document):
        rendition = Rendition(mock_book, "viewer")
        rendition.current_chapter_index = 1
        with patch.object(rendition, 'display') as mock_display:
            rendition.previous_chapter()
            assert rendition.current_chapter_index == 0
            mock_display.assert_called_once_with(mock_book.spine[0])

def test_embed_asset(mock_book, mock_document):
    """Test that _embed_asset correctly creates a data URI."""
    with patch("imposition.rendition.document", mock_document):
        rendition = Rendition(mock_book, "viewer")
        element = ET.Element('img', {'src': '../images/cover.jpg'})
        chapter_path = "OEBPS/chapter1.xhtml"
        # This is the expected path after normalization
        expected_asset_path = "images/cover.jpg"

        mock_book.zip_file.read.return_value = b'fake image data'
        with patch('mimetypes.guess_type', return_value=('image/jpeg', None)) as mock_guess_type:
            rendition._embed_asset(element, 'src', chapter_path)

        mock_guess_type.assert_called_once_with(expected_asset_path)
        mock_book.zip_file.read.assert_called_once_with(expected_asset_path)
        assert element.get('src').startswith('data:image/jpeg;base64,')
