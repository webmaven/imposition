from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET

import pytest

from imposition.rendition import Rendition
from imposition.book import Book
from tests.mocks import MockDOMAdapter


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
def mock_dom_adapter():
    """Fixture to create a MockDOMAdapter instance."""
    return MockDOMAdapter()


def test_rendition_initialization(mock_book, mock_dom_adapter):
    """Test that the Rendition class initializes correctly."""
    rendition = Rendition(mock_book, mock_dom_adapter, "viewer")
    assert rendition.book is mock_book
    assert rendition.dom_adapter is mock_dom_adapter
    assert rendition.target_id == "viewer"
    assert rendition.target_element is not None
    assert rendition.iframe is not None
    assert rendition.iframe.tag_name == 'iframe'


def test_display_toc(mock_book, mock_dom_adapter):
    """Test that the display_toc method correctly generates the TOC."""
    rendition = Rendition(mock_book, mock_dom_adapter, "viewer")
    rendition.display_toc()

    toc_container = mock_dom_adapter.get_element_by_id("toc")
    assert toc_container.innerHTML == ''
    # Expect 2 children: <h3> and <ul>
    assert len(toc_container.children) == 2

    header_element = toc_container.children[0]
    assert header_element.tag_name == 'h3'
    assert header_element.textContent == 'Contents'

    ul_element = toc_container.children[1]
    assert ul_element.tag_name == 'ul'
    assert len(ul_element.children) == len(mock_book.toc)

    # Check the generated links
    li_element = ul_element.children[0]
    a_element = li_element.children[0]
    assert a_element.textContent == "Chapter 1"
    assert a_element.href == "#"


def test_display_first_chapter(mock_book, mock_dom_adapter):
    """Test displaying the first chapter by default."""
    rendition = Rendition(mock_book, mock_dom_adapter, "viewer")
    rendition.display()
    mock_book.zip_file.read.assert_called_once_with(mock_book.spine[0])
    assert "data:text/html;base64," in rendition.iframe.src


def test_display_specific_chapter(mock_book, mock_dom_adapter):
    """Test displaying a specific chapter by URL."""
    rendition = Rendition(mock_book, mock_dom_adapter, "viewer")
    chapter_url = "OEBPS/chapter2.xhtml"
    rendition.display(chapter_url)
    mock_book.zip_file.read.assert_called_once_with(chapter_url)
    assert "data:text/html;base64," in rendition.iframe.src


def test_display_with_anchor(mock_book, mock_dom_adapter):
    """Test that displaying a chapter with an anchor sets the iframe onload property."""
    rendition = Rendition(mock_book, mock_dom_adapter, "viewer")
    chapter_url = "OEBPS/chapter1.xhtml#section1"
    rendition.display(chapter_url)
    assert rendition.iframe.onload == "this.contentWindow.location.hash = '#section1'"


def test_next_chapter(mock_book, mock_dom_adapter):
    """Test navigating to the next chapter."""
    rendition = Rendition(mock_book, mock_dom_adapter, "viewer")
    rendition.current_chapter_index = 0
    with patch.object(rendition, 'display') as mock_display:
        rendition.next_chapter()
        assert rendition.current_chapter_index == 1
        mock_display.assert_called_once_with(mock_book.spine[1])


def test_previous_chapter(mock_book, mock_dom_adapter):
    """Test navigating to the previous chapter."""
    rendition = Rendition(mock_book, mock_dom_adapter, "viewer")
    rendition.current_chapter_index = 1
    with patch.object(rendition, 'display') as mock_display:
        rendition.previous_chapter()
        assert rendition.current_chapter_index == 0
        mock_display.assert_called_once_with(mock_book.spine[0])


def test_embed_asset(mock_book, mock_dom_adapter):
    """Test that _embed_asset correctly creates a data URI."""
    rendition = Rendition(mock_book, mock_dom_adapter, "viewer")
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

def test_setup_controls(mock_book, mock_dom_adapter):
    """Test that setup_controls correctly attaches event listeners."""
    rendition = Rendition(mock_book, mock_dom_adapter, "viewer")
    rendition.setup_controls("prev", "next")

    prev_button = mock_dom_adapter.get_element_by_id("prev")
    next_button = mock_dom_adapter.get_element_by_id("next")

    assert prev_button.onclick is not None
    assert next_button.onclick is not None
    # Initially on first chapter, so prev should be disabled
    assert prev_button.disabled is True
    assert next_button.disabled is False

def test_update_controls_highlighting(mock_book, mock_dom_adapter):
    """Test that update_controls correctly highlights the active TOC link."""
    rendition = Rendition(mock_book, mock_dom_adapter, "viewer")
    rendition.display_toc()

    # Initially chapter 1 is active (index 0)
    rendition.current_chapter_index = 0
    rendition.update_controls()

    assert rendition.toc_links[0][0].className == 'active'
    assert rendition.toc_links[1][0].className == ''

    # Change to chapter 2
    rendition.current_chapter_index = 1
    rendition.update_controls()

    assert rendition.toc_links[0][0].className == ''
    assert rendition.toc_links[1][0].className == 'active'
