import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock the 'js' module before importing the script that uses it
sys.modules["js"] = MagicMock()

# Add the 'src' directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
# Also add the project root to find run_imposition
sys.path.insert(0, str(project_root))

import run_imposition  # noqa: E402

# --- Test Fixtures and Mocks ---

@pytest.fixture
def epub_bytes():
    """Fixture to provide the content of the test EPUB file."""
    epub_path = project_root / "test_book.epub"
    return epub_path.read_bytes()

class MockJsProxy:
    """A mock to simulate pyodide.JsProxy for byte arrays."""
    def __init__(self, data):
        self._data = data

    def to_py(self):
        return self._data

@pytest.fixture
def mock_js_object(epub_bytes):
    """Fixture to create a mock of the global `js` object."""
    mock_js = MagicMock()

    # Mock the pyfetch response chain
    mock_response = AsyncMock()
    mock_response.bytes = AsyncMock(return_value=MockJsProxy(epub_bytes))
    mock_js.pyfetch = AsyncMock(return_value=mock_response)

    # Mock the window object that the script attaches the rendition to
    mock_js.window = MagicMock()

    return mock_js

# --- Test Case ---

@pytest.mark.asyncio
async def test_main_application_flow(mock_js_object):
    """
    Tests the main logic of run_imposition.py by patching the `js` object
    and the Rendition class to ensure they are used as expected.
    """
    # Patch the `js` object and the `Rendition` class within the run_imposition module
    with patch('run_imposition.js', mock_js_object), \
         patch('run_imposition.Book', autospec=True) as mock_book_class, \
         patch('run_imposition.Rendition', autospec=True) as mock_rendition_class:

        # Get the mock instances that will be created by the script
        mock_book_instance = mock_book_class.return_value
        # Give the mock book a spine so the script can access it
        mock_book_instance.spine = ["chapter1.xhtml"]
        mock_rendition_instance = mock_rendition_class.return_value

        # --- Act ---
        # Run the main function from the script
        await run_imposition.main()

        # --- Assert ---
        # 1. Verify that the EPUB file was fetched
        mock_js_object.pyfetch.assert_awaited_once_with("test_book.epub")

        # 2. Verify that the Book object was instantiated with the EPUB content
        # The mock_js_object is configured to return the bytes from the epub_bytes fixture
        epub_content = mock_js_object.pyfetch.return_value.bytes.return_value.to_py()
        mock_book_class.assert_called_once_with(epub_content)

        # 3. Verify that the Rendition object was instantiated with the book and viewer ID
        mock_rendition_class.assert_called_once_with(mock_book_instance, "viewer")

        # 4. Verify that the rendition instance was attached to the mock window
        assert mock_js_object.window.rendition is mock_rendition_instance

        # 5. Verify that the TOC and the first chapter were displayed
        mock_rendition_instance.display_toc.assert_called_once_with()
        mock_rendition_instance.display.assert_called_once_with("chapter1.xhtml")
