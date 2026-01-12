import asyncio
import js
from imposition.book import Book
from imposition.rendition import Rendition

async def main():
    print("Starting Python script")
    response = await js.pyfetch("test_book.epub")
    epub_bytes_proxy = await response.bytes()
    epub_bytes = epub_bytes_proxy.to_py()

    book = Book(epub_bytes)
    rendition = Rendition(book, "viewer")

    js.window.rendition = rendition

    rendition.display_toc()
    rendition.display(book.spine[0])

if __name__ == "__main__":
    asyncio.run(main())
