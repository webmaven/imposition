import asyncio
import js
from pyodide.ffi import JsProxy
from imposition.book import Book
from imposition.rendition import Rendition

async def main() -> None:
    print("Starting Python script")
    response: JsProxy = await js.pyfetch("test_book.epub")
    epub_bytes_proxy: JsProxy = await response.bytes()
    epub_bytes: bytes = epub_bytes_proxy.to_py()

    book: Book = Book(epub_bytes)
    rendition: Rendition = Rendition(book, "viewer")

    js.window.rendition = rendition

    rendition.display_toc()
    rendition.display(book.spine[0])

if __name__ == "__main__":
    asyncio.run(main())
