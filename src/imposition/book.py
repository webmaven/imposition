import zipfile
import xml.etree.ElementTree as ET
import io
import posixpath
from typing import List, Dict, Optional

from .exceptions import InvalidEpubError, MissingContainerError


class Book:
    """
    Parses and provides access to the contents of an EPUB file.

    This class takes the binary content of an EPUB file, parses its
    structure, and provides methods to access its table of contents and
    spine.
    """

    def __init__(self, epub_bytes: bytes) -> None:
        """
        Initializes the Book object from a bytes object of the EPUB file.

        :param epub_bytes: The binary content of the EPUB file.
        :type epub_bytes: bytes
        :raises InvalidEpubError: If the file is not a valid ZIP archive or if
            the EPUB structure is invalid.
        :raises MissingContainerError: If the META-INF/container.xml file is
            not found.
        """
        epub_file = io.BytesIO(epub_bytes)
        try:
            self.zip_file: zipfile.ZipFile = zipfile.ZipFile(epub_file, "r")
        except zipfile.BadZipFile as e:
            raise InvalidEpubError("The file is not a valid ZIP archive.") from e

        # Validate mimetype file
        try:
            mimetype_content: bytes = self.zip_file.read("mimetype")
            if mimetype_content.strip() != b"application/epub+zip":
                raise InvalidEpubError(
                    f"Invalid mimetype: {mimetype_content.decode('utf-8', errors='replace')}"
                )
        except KeyError as e:
            raise InvalidEpubError("mimetype file not found in the EPUB file.") from e

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
        rootfile_element: Optional[ET.Element] = root.find("c:rootfiles/c:rootfile", ns)
        if rootfile_element is None:
            raise InvalidEpubError("Could not find rootfile element in container.xml.")

        opf_path: Optional[str] = rootfile_element.get("full-path")
        if not opf_path:
            raise InvalidEpubError("Rootfile element in container.xml is missing the 'full-path' attribute.")

        self.opf_path: str = opf_path
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
        """
        Returns the table of contents.

        :return: A list of dictionaries, where each dictionary represents a
            table of contents item with 'title' and 'url' keys.
        :rtype: List[Dict[str, str]]
        """
        return self.toc

    def _parse_toc(self) -> List[Dict[str, str]]:
        """
        Parses the toc.ncx file to get the table of contents.
        """
        ns: Dict[str, str] = {"opf": "http://www.idpf.org/2007/opf"}

        spine_element: Optional[ET.Element] = self.opf_root.find("opf:spine", ns)
        if spine_element is None:
            raise InvalidEpubError("Could not find spine element in OPF file.")
        toc_id: Optional[str] = spine_element.get("toc")
        if not toc_id:
            return []  # No TOC defined

        toc_item_element: Optional[ET.Element] = self.opf_root.find(
            f"opf:manifest/opf:item[@id='{toc_id}']", ns
        )
        if toc_item_element is None:
            raise InvalidEpubError(f"TOC item with id '{toc_id}' not found in manifest.")

        toc_href: Optional[str] = toc_item_element.get("href")
        if not toc_href:
            raise InvalidEpubError(f"TOC item '{toc_id}' has no href attribute.")

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

        spine_ids_raw = [item.get("idref") for item in spine_element.findall("opf:itemref", ns)]
        spine_ids: List[str] = [idref for idref in spine_ids_raw if idref is not None]

        try:
            spine_paths: List[str] = [manifest[id] for id in spine_ids]
        except KeyError as e:
            raise InvalidEpubError(f"Item in spine not found in manifest: {e}") from e

        return spine_paths
