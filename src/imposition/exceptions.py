class ImpositionError(Exception):
    """Base class for all exceptions raised by the imposition library."""

    pass


class InvalidEpubError(ImpositionError):
    """
    Exception raised for errors related to the EPUB file format.

    This can include issues with the ZIP structure, XML parsing, or missing
    required components in the EPUB container.
    """

    pass


class MissingContainerError(InvalidEpubError):
    """
    Exception raised when the META-INF/container.xml file is missing.

    This file is essential for locating the root OPF file of the EPUB.
    """

    pass
