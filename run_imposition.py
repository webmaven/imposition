print("Starting Python script")
from pyodide.http import pyfetch
from imposition.book import Book
from imposition.rendition import Rendition

response = await pyfetch("test_book.epub")
epub_bytes = await response.bytes()

book = Book(epub_bytes)
from js import window

rendition = Rendition(book, "viewer")
rendition.display()

# Get TOC and display it
toc = book.get_toc()
window.displayToc(toc)
