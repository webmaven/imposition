import pytest
from imposition.book import Book
import io
import zipfile
import xml.etree.ElementTree as ET

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

@pytest.fixture
def epub_missing_container():
    return create_epub_bytes({'mimetype': 'application/epub+zip'})

@pytest.fixture
def epub_malformed_opf():
    container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    opf_content = "this is not valid XML"
    return create_epub_bytes({
        'mimetype': 'application/epub+zip',
        'META-INF/container.xml': container_xml,
        'OEBPS/content.opf': opf_content
    })

@pytest.fixture
def epub_malformed_ncx():
    container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    opf_content = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="pub-id" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>Test Book</dc:title>
    <dc:creator>Test Author</dc:creator>
    <dc:identifier id="pub-id">12345</dc:identifier>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="chapter1"/>
  </spine>
</package>
"""
    ncx_content = "this is not valid XML"
    return create_epub_bytes({
        'mimetype': 'application/epub+zip',
        'META-INF/container.xml': container_xml,
        'OEBPS/content.opf': opf_content,
        'OEBPS/toc.ncx': ncx_content
    })

def test_missing_container_xml(epub_missing_container):
    with pytest.raises(KeyError):
        Book(epub_missing_container)

def test_malformed_opf(epub_malformed_opf):
    with pytest.raises(ET.ParseError):
        Book(epub_malformed_opf)

def test_malformed_ncx(epub_malformed_ncx):
    with pytest.raises(ET.ParseError):
        Book(epub_malformed_ncx)
