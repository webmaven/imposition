from js import document
import xml.etree.ElementTree as ET
import base64
import os
import mimetypes

class Rendition:
    def __init__(self, book, target_id):
        self.book = book
        self.target_id = target_id
        self.target_element = document.getElementById(self.target_id)
        self.current_chapter_index = 0

        self.iframe = document.createElement('iframe')
        self.iframe.name = "epub-rendition"
        self.iframe.style.width = '100%'
        self.iframe.style.height = '100%'
        self.iframe.style.border = '2px solid red'
        self.target_element.innerHTML = ''
        self.target_element.appendChild(self.iframe)

    def display(self, chapter_href):
        if not self.book.spine:
            return

        try:
            self.current_chapter_index = self.book.spine.index(chapter_href)
        except ValueError:
            pass

        chapter_content = self.book.zip_file.read(chapter_href)

        try:
            ET.register_namespace("", "http://www.w3.org/1999/xhtml")
            root = ET.fromstring(chapter_content)
        except ET.ParseError as e:
            print(f"Error parsing chapter content: {e}")
            self.target_element.textContent = "Error loading chapter: Could not parse XML."
            return

        head = root.find(".//{http://www.w3.org/1999/xhtml}head")
        if head is not None:
            for link in head.findall(".//{http://www.w3.org/1999/xhtml}link[@rel='stylesheet']"):
                head.remove(link)
            for style in head.findall(".//{http://www.w3.org/1999/xhtml}style"):
                head.remove(style)
            style_element = ET.Element('style')
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

        final_html = "<!DOCTYPE html>" + ET.tostring(root, method='html').decode('utf-8')
        encoded_html = base64.b64encode(final_html.encode('utf-8')).decode('utf-8')
        self.iframe.src = f"data:text/html;base64,{encoded_html}"

    def display_toc(self):
        toc_element = document.getElementById("toc")
        if not toc_element:
            return

        toc_list = document.createElement("ul")
        for item in self.book.toc:
            list_item = document.createElement("li")
            link = document.createElement("a")
            link.textContent = item['label']
            link.href = "#"

            def click_handler(event, href=item['href']):
                event.preventDefault()
                self.display(href)

            link.addEventListener("click", click_handler)

            list_item.appendChild(link)
            toc_list.appendChild(list_item)

        toc_element.innerHTML = ""
        toc_element.appendChild(toc_list)

    def _embed_asset(self, element, attribute, chapter_path):
        asset_path = element.get(attribute)
        if not asset_path or asset_path.startswith(('data:', 'http:', 'https:')):
            return

        if asset_path.endswith('.css'):
            return

        full_asset_path = os.path.normpath(os.path.join(os.path.dirname(chapter_path), asset_path))

        try:
            asset_content = self.book.zip_file.read(full_asset_path)
            mime_type, _ = mimetypes.guess_type(full_asset_path)
            if mime_type:
                encoded_asset = base64.b64encode(asset_content).decode('utf-8')
                data_uri = f"data:{mime_type};base64,{encoded_asset}"
                element.set(attribute, data_uri)
        except KeyError:
            print(f"Asset not found: {full_asset_path}")
            pass

    def next_chapter(self, event=None):
        if self.current_chapter_index < len(self.book.spine) - 1:
            self.current_chapter_index += 1
            self.display(self.book.spine[self.current_chapter_index])

    def previous_chapter(self, event=None):
        if self.current_chapter_index > 0:
            self.current_chapter_index -= 1
            self.display(self.book.spine[self.current_chapter_index])
