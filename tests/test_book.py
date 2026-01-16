import pytest
from imposition.book import Book
from imposition.exceptions import InvalidEpubError, MissingContainerError
import io
import zipfile

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

def test_parse_spine(book):
    assert isinstance(book.spine, list)
    assert len(book.spine) > 0
    assert all(isinstance(item, str) for item in book.spine)

def create_epub_bytes(files):
    """Creates an in-memory EPUB file (zip archive) from a dictionary of files."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for path, content in files.items():
            zip_file.writestr(path, content)
    return zip_buffer.getvalue()

def test_invalid_zip_file():
    with pytest.raises(InvalidEpubError, match="not a valid ZIP archive"):
        Book(b"this is not a zip file")

def test_missing_container_xml():
    epub_bytes = create_epub_bytes({'mimetype': 'application/epub+zip'})
    with pytest.raises(MissingContainerError, match="META-INF/container.xml not found"):
        Book(epub_bytes)

def test_malformed_container_xml():
    epub_bytes = create_epub_bytes({
        'mimetype': 'application/epub+zip',
        'META-INF/container.xml': 'this is not valid XML'
    })
    with pytest.raises(InvalidEpubError, match="Could not parse META-INF/container.xml"):
        Book(epub_bytes)

def test_missing_rootfile_in_container():
    container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
  </rootfiles>
</container>
"""
    epub_bytes = create_epub_bytes({
        'mimetype': 'application/epub+zip',
        'META-INF/container.xml': container_xml
    })
    with pytest.raises(InvalidEpubError, match="Could not find rootfile element"):
        Book(epub_bytes)

def test_missing_opf_file():
    container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    epub_bytes = create_epub_bytes({
        'mimetype': 'application/epub+zip',
        'META-INF/container.xml': container_xml
    })
    with pytest.raises(InvalidEpubError, match="OPF file not found"):
        Book(epub_bytes)

def test_malformed_opf_file():
    container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    opf_content = "this is not valid XML"
    epub_bytes = create_epub_bytes({
        'mimetype': 'application/epub+zip',
        'META-INF/container.xml': container_xml,
        'OEBPS/content.opf': opf_content
    })
    with pytest.raises(InvalidEpubError, match="Could not parse OPF file"):
        Book(epub_bytes)

def test_spine_item_not_in_manifest():
    container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="pub-id" version="2.0">
  <metadata/>
  <manifest>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="non-existent-item"/>
  </spine>
</package>
"""
    epub_bytes = create_epub_bytes({
        'mimetype': 'application/epub+zip',
        'META-INF/container.xml': container_xml,
        'OEBPS/content.opf': opf_content
    })
    with pytest.raises(InvalidEpubError, match="Item in spine not found in manifest"):
        Book(epub_bytes)

def test_missing_mimetype_file():
    epub_bytes = create_epub_bytes({'META-INF/container.xml': 'some content'})
    with pytest.raises(InvalidEpubError, match="mimetype file not found"):
        Book(epub_bytes)

def test_invalid_mimetype_content():
    epub_bytes = create_epub_bytes({'mimetype': 'text/plain'})
    with pytest.raises(InvalidEpubError, match="Invalid mimetype: text/plain"):
        Book(epub_bytes)
