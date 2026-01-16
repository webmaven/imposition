from typing import Any, Callable, Dict, List, Optional
from unittest.mock import Mock, MagicMock

class MockDOMElement:
    """A mock DOM element for testing."""
    def __init__(self, tag_name: str) -> None:
        self.tag_name: str = tag_name
        self.children: List[MockDOMElement] = []
        self.attributes: Dict[str, str] = {}
        self.style = MagicMock()
        self.innerHTML: str = ""
        self.textContent: str = ""
        self.href: str = "#"
        self.onclick: Optional[Callable[[Any], None]] = None
        self.onload: str = ""
        self.src: str = ""
        self.disabled: bool = False
        self.className: str = ""
        self.preventDefault: Mock = Mock()

    def appendChild(self, child: "MockDOMElement") -> None:
        self.children.append(child)

    def setAttribute(self, name: str, value: str) -> None:
        self.attributes[name] = value

class MockDOMAdapter:
    """A mock DOM adapter for testing."""
    def __init__(self) -> None:
        self.elements: Dict[str, MockDOMElement] = {}

    def get_element_by_id(self, element_id: str) -> MockDOMElement:
        if element_id not in self.elements:
            self.elements[element_id] = MockDOMElement("div")
        return self.elements[element_id]

    def create_element(self, tag_name: str) -> MockDOMElement:
        return MockDOMElement(tag_name)

    def create_proxy(self, handler: Callable[..., Any]) -> Callable[..., Any]:
        return handler
