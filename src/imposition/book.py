import zipfile
import xml.etree.ElementTree as ET
import io
import posixpath
from typing import List, Dict

class Book:
    def __init__(self, epub_bytes: bytes) -> None:
        """
        Initializes the Book object from a bytes object of the EPUB file.
        """
        epub_file = io.BytesIO(epub_bytes)
        self.zip_file: zipfile.ZipFile = zipfile.ZipFile(epub_file, 'r')

        # Find the .opf file from container.xml
        container_xml: bytes = self.zip_file.read('META-INF/container.xml')
        root: ET.Element = ET.fromstring(container_xml)
        ns: Dict[str, str] = {'c': 'urn:oasis:names:tc:opendocument:xmlns:container'}
        opf_path_element = root.find('c:rootfiles/c:rootfile', ns)
        if opf_path_element is None:
            raise ValueError("Could not find rootfile in container.xml")
        opf_path = opf_path_element.get('full-path')
        if opf_path is None:
            raise ValueError("Rootfile element has no full-path attribute")
        self.opf_path: str = opf_path
        self.opf_dir: str = posixpath.dirname(self.opf_path)

        self.spine: List[str] = self._parse_spine()
        self.toc: List[Dict[str, str]] = self._parse_toc()

    def get_toc(self) -> List[Dict[str, str]]:
        return self.toc

    def _parse_toc(self) -> List[Dict[str, str]]:
        """
        Parses the toc.ncx file to get the table of contents.
        """
        opf_xml: bytes = self.zip_file.read(self.opf_path)
        root: ET.Element = ET.fromstring(opf_xml)
        ns: Dict[str, str] = {'opf': 'http://www.idpf.org/2007/opf'}

        # Find the toc.ncx path from the manifest
        spine_element = root.find('opf:spine', ns)
        if spine_element is None:
            return []
        toc_id = spine_element.get('toc')
        if not toc_id:
            return []
        toc_item = root.find(f"opf:manifest/opf:item[@id='{toc_id}']", ns)
        if toc_item is None:
            return []
        toc_href = toc_item.get('href')
        if not toc_href:
            return []
        toc_path: str = posixpath.normpath(posixpath.join(self.opf_dir, toc_href))

        # Parse the toc.ncx file
        toc_xml: bytes = self.zip_file.read(toc_path)
        toc_root: ET.Element = ET.fromstring(toc_xml)
        ns_ncx: Dict[str, str] = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}

        toc: List[Dict[str, str]] = []
        for nav_point in toc_root.findall('.//ncx:navPoint', ns_ncx):
            title_element = nav_point.find('ncx:navLabel/ncx:text', ns_ncx)
            content_element = nav_point.find('ncx:content', ns_ncx)
            if title_element is not None and title_element.text and content_element is not None:
                src = content_element.get('src')
                if src:
                    title = title_element.text
                    # The src is relative to the toc.ncx file, so create the full path
                    full_path: str = posixpath.normpath(posixpath.join(posixpath.dirname(toc_path), src))
                    toc.append({'title': title, 'url': full_path})

        return toc

    def _parse_spine(self) -> List[str]:
        """
        Parses the .opf file to find the book's content files in reading order.
        """
        opf_xml: bytes = self.zip_file.read(self.opf_path)
        root: ET.Element = ET.fromstring(opf_xml)
        ns: Dict[str, str] = {'opf': 'http://www.idpf.org/2007/opf'}

        manifest: Dict[str, str] = {}
        for item in root.findall('opf:manifest/opf:item', ns):
            item_id = item.get('id')
            href = item.get('href')
            if item_id and href:
                # The href is relative to the .opf file, so create the full path
                full_path: str = posixpath.join(self.opf_dir, href)
                # Normalize the path to handle things like '..'
                normalized_path: str = posixpath.normpath(full_path)
                manifest[item_id] = normalized_path

        spine_ids_raw = [item.get('idref') for item in root.findall('opf:spine/opf:itemref', ns)]
        spine_ids: List[str] = [idref for idref in spine_ids_raw if idref is not None]

        spine_paths: List[str] = [manifest[id] for id in spine_ids if id in manifest]

        return spine_paths
