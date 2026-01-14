from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, Optional

from js import document
from pyodide.ffi import create_proxy, JsProxy
import xml.etree.ElementTree as ET
import base64
import posixpath
import mimetypes

if TYPE_CHECKING:
    from .book import Book


class Rendition:
    """
    Renders an EPUB file into a web-based reader interface.

    This class handles the display of the EPUB's table of contents and
    chapters, and provides navigation between them.
    """

    def __init__(self, book: Book, target_id: str) -> None:
        """
        Initializes the Rendition object.

        :param book: An initialized Book object.
        :type book: Book
        :param target_id: The ID of the HTML element where the EPUB content
            will be rendered.
        :type target_id: str
        """
        self.book: Book = book
        self.target_id: str = target_id
        self.target_element: JsProxy = document.getElementById(self.target_id)
        self.current_chapter_index: int = 0
        self.iframe: JsProxy = document.createElement('iframe')
        self.iframe.style.width = '100%'
        self.iframe.style.height = '100%'
        self.iframe.style.border = 'none'

    def display_toc(self) -> None:
        """
        Renders the table of contents into the 'toc-container' element.
        """
        toc_container: JsProxy = document.getElementById('toc-container')
        toc_container.innerHTML = ''
        ul: JsProxy = document.createElement('ul')

        for item in self.book.toc:
            li: JsProxy = document.createElement('li')
            a: JsProxy = document.createElement('a')
            a.href = '#'
            a.textContent = item['title']

            # Define a handler function to be proxied
            def create_handler(url: str) -> Callable[[JsProxy], None]:
                def handler(event: JsProxy) -> None:
                    event.preventDefault()
                    self.display(url)
                return handler

            # Create a proxy for the onclick event handler
            a.onclick = create_proxy(create_handler(item['url']))

            li.appendChild(a)
            ul.appendChild(li)

        toc_container.appendChild(ul)


    def display(self, chapter_url: Optional[str] = None) -> None:
        """
        Displays a specific chapter in the rendition iframe.

        If no chapter URL is provided, it displays the first chapter in the
        spine. It also handles embedding of assets like images.

        :param chapter_url: The URL of the chapter to display. Can include an
            anchor.
        :type chapter_url: Optional[str]
        """
        if not self.book.spine:
            return
        anchor: Optional[str] = None
        chapter_href: str
        if chapter_url and '#' in chapter_url:
            anchor = chapter_url.split('#')[1]
            chapter_href = chapter_url.split('#')[0]
        elif chapter_url:
            chapter_href = chapter_url
        else:
            chapter_href = self.book.spine[0]

        chapter_content: bytes = self.book.zip_file.read(chapter_href)

        try:
            ET.register_namespace("", "http://www.w3.org/1999/xhtml")
            root: ET.Element = ET.fromstring(chapter_content)
        except ET.ParseError as e:
            print(f"Error parsing chapter content: {e}")
            self.target_element.textContent = "Error loading chapter: Could not parse XML."
            return

        head: Optional[ET.Element] = root.find(".//{http://www.w3.org/1999/xhtml}head")
        if head is not None:
            for link in head.findall(".//{http://www.w3.org/1999/xhtml}link[@rel='stylesheet']"):
                head.remove(link)
            for style in head.findall(".//{http://www.w3.org/1999/xhtml}style"):
                head.remove(style)
            style_element: ET.Element = ET.Element('style')
            style_element.text = 'body { margin: 0; }'
            head.append(style_element)

        for element in root.iter():
            if 'style' in element.attrib:
                del element.attrib['style']

        for element in root.findall(".//*[@src]"):
            self._embed_asset(element, 'src', chapter_href)
        for element in root.findall(".//*[@href]"):
            if not element.get('href', '').endswith('.css'):
                 self._embed_asset(element, 'href', chapter_href)

        final_html: str = "<!DOCTYPE html>" + ET.tostring(root, method='html').decode('utf-8')
        encoded_html: str = base64.b64encode(final_html.encode('utf-8')).decode('utf-8')
        self.iframe.src = f"data:text/html;base64,{encoded_html}"

        if anchor:
            self.iframe.onload = f"this.contentWindow.location.hash = '#{anchor}'"

        self.target_element.innerHTML = ''
        self.target_element.appendChild(self.iframe)

    def _embed_asset(self, element: ET.Element, attribute: str, chapter_path: str) -> None:
        asset_path: Optional[str] = element.get(attribute)
        if not asset_path or asset_path.startswith(('data:', 'http:', 'https:')):
            return

        if asset_path.endswith('.css'):
            return

        full_asset_path: str = posixpath.normpath(posixpath.join(posixpath.dirname(chapter_path), asset_path))

        try:
            asset_content: bytes = self.book.zip_file.read(full_asset_path)
            mime_type: Optional[str]
            mime_type, _ = mimetypes.guess_type(full_asset_path)
            if mime_type:
                encoded_asset: str = base64.b64encode(asset_content).decode('utf-8')
                data_uri: str = f"data:{mime_type};base64,{encoded_asset}"
                element.set(attribute, data_uri)
        except KeyError:
            print(f"Asset not found: {full_asset_path}")
            pass

    def next_chapter(self, event: Optional[Any] = None) -> None:
        """
        Displays the next chapter in the book's spine.

        :param event: An optional event object (e.g., from a button click).
        :type event: Optional[Any]
        """
        if self.current_chapter_index < len(self.book.spine) - 1:
            self.current_chapter_index += 1
            self.display(self.book.spine[self.current_chapter_index])

    def previous_chapter(self, event: Optional[Any] = None) -> None:
        """
        Displays the previous chapter in the book's spine.

        :param event: An optional event object (e.g., from a button click).
        :type event: Optional[Any]
        """
        if self.current_chapter_index > 0:
            self.current_chapter_index -= 1
            self.display(self.book.spine[self.current_chapter_index])
