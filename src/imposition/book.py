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
        self.toc = self._parse_toc()

    def _parse_toc(self):
        """
        Parses the toc.ncx file to get the table of contents.
        """
        opf_xml = self.zip_file.read(self.opf_path)
        root = ET.fromstring(opf_xml)
        ns_opf = {'opf': 'http://www.idpf.org/2007/opf'}

        # Find the manifest item id for the NCX file.
        # First, try the spine's 'toc' attribute.
        spine_tag = root.find('opf:spine', ns_opf)
        toc_id = spine_tag.get('toc') if spine_tag is not None else None

        ncx_path = None
        manifest_items = root.findall('opf:manifest/opf:item', ns_opf)

        if toc_id:
            for item in manifest_items:
                if item.get('id') == toc_id:
                    href = item.get('href')
                    ncx_path = os.path.normpath(os.path.join(self.opf_dir, href))
                    break

        # If not found, try to find by media-type
        if not ncx_path:
            for item in manifest_items:
                if item.get('media-type') == "application/x-dtbncx+xml":
                    href = item.get('href')
                    ncx_path = os.path.normpath(os.path.join(self.opf_dir, href))
                    break

        if not ncx_path:
             return []

        try:
            ncx_xml = self.zip_file.read(ncx_path)
            root_ncx = ET.fromstring(ncx_xml)
            ns_ncx = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}

            toc_list = []

            # Find the navMap to start parsing from
            nav_map = root_ncx.find('ncx:navMap', ns_ncx)
            if nav_map is not None:
                self._parse_nav_points(nav_map, toc_list, ns_ncx)

            return toc_list
        except (KeyError, ET.ParseError):
            # If the ncx file is missing or malformed
            return []

    def _parse_nav_points(self, parent_element, toc_list, ns):
        """
        Recursively parses navPoint elements.
        """
        for nav_point in parent_element.findall('ncx:navPoint', ns):
            label_element = nav_point.find('ncx:navLabel/ncx:text', ns)
            if label_element is not None:
                label = label_element.text
                content_element = nav_point.find('ncx:content', ns)
                if content_element is not None:
                    src = content_element.get('src')
                    # The src path is relative to the .opf file's directory.
                    full_path = os.path.normpath(os.path.join(self.opf_dir, src))
                    toc_list.append({'label': label, 'href': full_path})

            # Recursively parse nested navPoints
            self._parse_nav_points(nav_point, toc_list, ns)

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
