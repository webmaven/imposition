from typing import Protocol, Any, Callable

from js import document
from pyodide.ffi import create_proxy as pyodide_create_proxy
from pyodide.ffi import JsProxy

class DOMElement(Protocol):
    """A protocol for DOM elements."""
    style: Any
    innerHTML: str
    textContent: str
    href: str
    onclick: Callable[[Any], None]
    onload: str
    src: str

    def appendChild(self, child: "DOMElement") -> None:
        ...

    def setAttribute(self, name: str, value: str) -> None:
        ...

class DOMAdapter(Protocol):
    """A protocol for DOM operations."""
    def get_element_by_id(self, element_id: str) -> DOMElement:
        ...

    def create_element(self, tag_name: str) -> DOMElement:
        ...

    def create_proxy(self, handler: Callable[..., Any]) -> Callable[..., Any]:
        ...

class PyodideDOMAdapter:
    """An implementation of the DOMAdapter protocol using Pyodide."""
    def get_element_by__id(self, element_id: str) -> JsProxy:
        return document.getElementById(element_id)

    def create_element(self, tag_name: str) -> JsProxy:
        return document.createElement(tag_name)

    def create_proxy(self, handler: Callable[..., Any]) -> Callable[..., Any]:
        return pyodide_create_proxy(handler)
