import zipfile
import xml.etree.ElementTree as ET
import io
import posixpath
from typing import List, Dict

from .exceptions import InvalidEpubError, MissingContainerError

class Book:
    def __init__(self, epub_bytes: bytes) -> None:
        """
        Initializes the Book object from a bytes object of the EPUB file.
        """
        epub_file = io.BytesIO(epub_bytes)
        try:
            self.zip_file: zipfile.ZipFile = zipfile.ZipFile(epub_file, "r")
        except zipfile.BadZipFile as e:
            raise InvalidEpubError("The file is not a valid ZIP archive.") from e

        # Find the .opf file from container.xml
        try:
            container_xml: bytes = self.zip_file.read("META-INF/container.xml")
        except KeyError as e:
            raise MissingContainerError(
                "META-INF/container.xml not found in the EPUB file."
            ) from e

        try:
            root: ET.Element = ET.fromstring(container_xml)
        except ET.ParseError as e:
            raise InvalidEpubError("Could not parse META-INF/container.xml.") from e

        ns: Dict[str, str] = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
        rootfile_element: ET.Element = root.find("c:rootfiles/c:rootfile", ns)
        if rootfile_element is None:
            raise InvalidEpubError("Could not find rootfile element in container.xml.")

        self.opf_path: str = rootfile_element.get("full-path")
        self.opf_dir: str = posixpath.dirname(self.opf_path)

        try:
            opf_xml: bytes = self.zip_file.read(self.opf_path)
        except KeyError as e:
            raise InvalidEpubError(f"OPF file not found: {self.opf_path}") from e
        try:
            self.opf_root: ET.Element = ET.fromstring(opf_xml)
        except ET.ParseError as e:
            raise InvalidEpubError(f"Could not parse OPF file: {self.opf_path}") from e

        self.spine: List[str] = self._parse_spine()
        self.toc: List[Dict[str, str]] = self._parse_toc()

    def get_toc(self) -> List[Dict[str, str]]:
        return self.toc

    def _parse_toc(self) -> List[Dict[str, str]]:
        """
        Parses the toc.ncx file to get the table of contents.
        """
        ns: Dict[str, str] = {"opf": "http://www.idpf.org/2007/opf"}

        # Find the toc.ncx path from the manifest
        spine_element: ET.Element = self.opf_root.find("opf:spine", ns)
        if spine_element is None:
            raise InvalidEpubError("Could not find spine element in OPF file.")
        toc_id: str = spine_element.get("toc")
        if not toc_id:
            return []  # No TOC defined

        toc_item_element: ET.Element = self.opf_root.find(
            f"opf:manifest/opf:item[@id='{toc_id}']", ns
        )
        if toc_item_element is None:
            raise InvalidEpubError(f"TOC item with id '{toc_id}' not found in manifest.")
        toc_href: str = toc_item_element.get("href")
        toc_path: str = posixpath.normpath(posixpath.join(self.opf_dir, toc_href))

        # Parse the toc.ncx file
        try:
            toc_xml: bytes = self.zip_file.read(toc_path)
        except KeyError as e:
            raise InvalidEpubError(f"TOC file not found: {toc_path}") from e

        try:
            toc_root: ET.Element = ET.fromstring(toc_xml)
        except ET.ParseError as e:
            raise InvalidEpubError(f"Could not parse TOC file: {toc_path}") from e

        ns_ncx: Dict[str, str] = {"ncx": "http://www.daisy.org/z3986/2005/ncx/"}

        toc: List[Dict[str, str]] = []
        for nav_point in toc_root.findall(".//ncx:navPoint", ns_ncx):
            title: str = nav_point.find("ncx:navLabel/ncx:text", ns_ncx).text
            src: str = nav_point.find("ncx:content", ns_ncx).get("src")
            # The src is relative to the toc.ncx file, so create the full path
            full_path: str = posixpath.normpath(
                posixpath.join(posixpath.dirname(toc_path), src)
            )
            toc.append({"title": title, "url": full_path})

        return toc

    def _parse_spine(self) -> List[str]:
        """
        Parses the .opf file to find the book's content files in reading order.
        """
        ns: Dict[str, str] = {"opf": "http://www.idpf.org/2007/opf"}

        manifest: Dict[str, str] = {}
        manifest_element = self.opf_root.find("opf:manifest", ns)
        if manifest_element is None:
            raise InvalidEpubError("Could not find manifest element in OPF file.")

        for item in manifest_element.findall("opf:item", ns):
            item_id = item.get("id")
            href = item.get("href")
            if not item_id or not href:
                continue  # Skip manifest items without id or href
            # The href is relative to the .opf file, so create the full path
            full_path: str = posixpath.join(self.opf_dir, href)
            # Normalize the path to handle things like '..'
            normalized_path: str = posixpath.normpath(full_path)
            manifest[item_id] = normalized_path

        spine_element = self.opf_root.find("opf:spine", ns)
        if spine_element is None:
            raise InvalidEpubError("Could not find spine element in OPF file.")

        spine_ids: List[str] = [
            item.get("idref") for item in spine_element.findall("opf:itemref", ns)
        ]

        try:
            spine_paths: List[str] = [manifest[id] for id in spine_ids]
        except KeyError as e:
            raise InvalidEpubError(f"Item in spine not found in manifest: {e}") from e

        return spine_paths
