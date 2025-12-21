from setuptools import setup, find_packages

setup(
    name="imposition",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    author="Jules",
    author_email="jules@example.com",
    description="A Python library for parsing and rendering EPUB files in Pyodide.",
)
