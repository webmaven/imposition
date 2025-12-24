print("Starting Python script")
from pyodide.http import pyfetch
from imposition.book import Book
from imposition.rendition import Rendition
import js

response = await pyfetch("test_book.epub")
epub_bytes = await response.bytes()

book = Book(epub_bytes)
rendition = Rendition(book, "viewer")
if book.spine:
    rendition.display(book.spine[0])
rendition.display_toc()

js.rendition = rendition
