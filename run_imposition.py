import asyncio
import js
from pyodide.ffi import JsProxy
from imposition.book import Book
from imposition.rendition import Rendition
from imposition.dom import PyodideDOMAdapter

async def main() -> None:
    response: JsProxy = await js.pyfetch("test_book.epub")
    epub_bytes_proxy: JsProxy = await response.bytes()
    epub_bytes: bytes = epub_bytes_proxy.to_py()

    book: Book = Book(epub_bytes)
    dom_adapter = PyodideDOMAdapter()
    rendition: Rendition = Rendition(book, dom_adapter, "viewer")

    js.window.rendition = rendition

    rendition.display_toc()
    rendition.display(book.spine[0])
