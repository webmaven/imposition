import sys
from unittest.mock import MagicMock

# Mock browser-specific modules before any other imports
sys.modules["js"] = MagicMock()
sys.modules["pyodide"] = MagicMock()
sys.modules["pyodide.ffi"] = MagicMock()
