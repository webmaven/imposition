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

    def display(self):
        if not self.book.spine:
            return

        chapter_href = self.book.spine[0]
        chapter_content = self.book.zip_file.read(chapter_href)

        try:
            ET.register_namespace("", "http://www.w3.org/1999/xhtml")
            root = ET.fromstring(chapter_content)
        except ET.ParseError as e:
            print(f"Error parsing chapter content: {e}")
            self.target_element.textContent = "Error loading chapter: Could not parse XML."
            return

        # Aggressively strip all CSS and add a margin reset
        head = root.find(".//{http://www.w3.org/1999/xhtml}head")
        if head is not None:
            # Remove all <link rel="stylesheet"> tags
            for link in head.findall(".//{http://www.w3.org/1999/xhtml}link[@rel='stylesheet']"):
                head.remove(link)
            # Remove all <style> tags
            for style in head.findall(".//{http://www.w3.org/1999/xhtml}style"):
                head.remove(style)

            # Add a style tag to reset the body margin
            style_element = ET.Element('style')
            style_element.text = 'body { margin: 0; }'
            head.append(style_element)

        # Also remove all inline style attributes from all elements
        for element in root.iter():
            if 'style' in element.attrib:
                del element.attrib['style']

        # Embed assets like images
        for element in root.findall(".//*[@src]"):
            self._embed_asset(element, 'src', chapter_href)
        for element in root.findall(".//*[@href]"):
            if not element.get('href', '').endswith('.css'):
                 self._embed_asset(element, 'href', chapter_href)

        # Create iframe with a visible border for debugging
        iframe = document.createElement('iframe')
        iframe.name = "epub-rendition"
        iframe.style.width = '100%'
        iframe.style.height = '100%'
        self.target_element.innerHTML = ''
        self.target_element.appendChild(iframe)

        # Add doctype and set content
        final_html = "<!DOCTYPE html>" + ET.tostring(root, method='html').decode('utf-8')
        iframe.srcdoc = final_html

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
