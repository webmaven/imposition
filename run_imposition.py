print("Starting Python script")
from pyodide.http import pyfetch
from imposition.book import Book
from imposition.rendition import Rendition

response = await pyfetch("test_book.epub")
epub_bytes = await response.bytes()

book = Book(epub_bytes)

rendition = Rendition(book, "viewer")
rendition.display()
rendition.display_toc()
