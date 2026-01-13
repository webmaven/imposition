import zipfile
import xml.etree.ElementTree as ET
import io
import posixpath
from typing import List, Dict, Any

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
        self.opf_path: str = root.find('c:rootfiles/c:rootfile', ns).get('full-path')
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
        toc_id: str = root.find('opf:spine', ns).get('toc')
        toc_href: str = root.find(f"opf:manifest/opf:item[@id='{toc_id}']", ns).get('href')
        toc_path: str = posixpath.normpath(posixpath.join(self.opf_dir, toc_href))

        # Parse the toc.ncx file
        toc_xml: bytes = self.zip_file.read(toc_path)
        toc_root: ET.Element = ET.fromstring(toc_xml)
        ns_ncx: Dict[str, str] = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}

        toc: List[Dict[str, str]] = []
        for nav_point in toc_root.findall('.//ncx:navPoint', ns_ncx):
            title: str = nav_point.find('ncx:navLabel/ncx:text', ns_ncx).text
            src: str = nav_point.find('ncx:content', ns_ncx).get('src')
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
            href: str = item.get('href')
            # The href is relative to the .opf file, so create the full path
            full_path: str = posixpath.join(self.opf_dir, href)
            # Normalize the path to handle things like '..'
            normalized_path: str = posixpath.normpath(full_path)
            manifest[item.get('id')] = normalized_path

        spine_ids: List[str] = [item.get('idref') for item in root.findall('opf:spine/opf:itemref', ns)]

        spine_paths: List[str] = [manifest[id] for id in spine_ids]

        return spine_paths
