import zipfile
import xml.etree.ElementTree as ET
import io
import os

class Book:
    def __init__(self, epub_bytes):
        """
        Initializes the Book object from a bytes object of the EPUB file.
        """
        epub_file = io.BytesIO(epub_bytes)
        self.zip_file = zipfile.ZipFile(epub_file, 'r')

        # Find the .opf file from container.xml
        container_xml = self.zip_file.read('META-INF/container.xml')
        root = ET.fromstring(container_xml)
        ns = {'c': 'urn:oasis:names:tc:opendocument:xmlns:container'}
        self.opf_path = root.find('c:rootfiles/c:rootfile', ns).get('full-path')
        self.opf_dir = os.path.dirname(self.opf_path)

        self.spine = self._parse_spine()

    def _parse_spine(self):
        """
        Parses the .opf file to find the book's content files in reading order.
        """
        opf_xml = self.zip_file.read(self.opf_path)
        root = ET.fromstring(opf_xml)
        ns = {'opf': 'http://www.idpf.org/2007/opf'}

        manifest = {}
        for item in root.findall('opf:manifest/opf:item', ns):
            href = item.get('href')
            # The href is relative to the .opf file, so create the full path
            full_path = os.path.join(self.opf_dir, href)
            # Normalize the path to handle things like '..'
            normalized_path = os.path.normpath(full_path)
            manifest[item.get('id')] = normalized_path

        spine_ids = [item.get('idref') for item in root.findall('opf:spine/opf:itemref', ns)]

        spine_paths = [manifest[id] for id in spine_ids]

        return spine_paths
