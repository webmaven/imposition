class ImpositionError(Exception):
    """Base class for exceptions in this module."""
    pass

class InvalidEpubError(ImpositionError):
    """Exception raised for errors in the EPUB file format."""
    pass

class MissingContainerError(InvalidEpubError):
    """Exception raised when META-INF/container.xml is missing."""
    pass
