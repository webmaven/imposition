# Imposition

This is the initial implementation of the `Imposition` library, a Python library intended to run under Pyodide for parsing and rendering EPUB files.

## Installation

This package is not yet available on PyPI. To install it, you must build the wheel from the source and then install it using `pip`:

```bash
hatch build
pip install dist/imposition-0.1.0-py3-none-any.whl
```

## Quick Start

The following example demonstrates how to load an EPUB file and render it in a web page.

```python
import asyncio
import js
from imposition.book import Book
from imposition.rendition import Rendition

async def main():
    response = await js.pyfetch("test_book.epub")
    epub_bytes_proxy = await response.bytes()
    epub_bytes = epub_bytes_proxy.to_py()

    book = Book(epub_bytes)
    rendition = Rendition(book, "viewer")

    js.window.rendition = rendition

    rendition.display_toc()
    rendition.display(book.spine[0])

if __name__ == "__main__":
    asyncio.run(main())
```

## Development Setup

To set up a development environment, clone the repository and use [Hatch](https://hatch.pypa.io/latest/) to manage dependencies.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/webmaven/imposition.git
   cd imposition
   ```

2. **Create the development environment:**
   ```bash
   hatch env create
   ```

3. **Activate the environment:**
   ```bash
   hatch shell
   ```

4. **Run tests:**
   ```bash
   pytest
   ```

## Building

To build the wheel for use with Pyodide, use the following command:

```bash
hatch build
```

This will create a `dist` directory with the wheel file (`imposition-0.1.0-py3-none-any.whl`).

## Testing

### Prerequisites

Before running tests, ensure you have the following installed:

1. **Python 3.13+** (or compatible version)
2. **pytest** and **pytest-playwright**:

   ```bash
   pip install pytest pytest-playwright
   ```

3. **Playwright browsers** (Chromium is required for E2E tests):

   ```bash
   python -m playwright install chromium
   ```

### Building the Package

The E2E tests require a built wheel package. Build it using:

```bash
pip install build
python -m build --wheel
```

This creates `dist/imposition-0.1.0-py3-none-any.whl`, which is loaded by the demo page during testing.

### Running Tests

Run all tests with:

```bash
python -m pytest -v
```

For more detailed output:

```bash
python -m pytest -vv
```

### Test Coverage

The current test suite includes:

- **E2E Test** (`tests/test_e2e.py`): Tests the complete workflow of loading an EPUB file in a browser using Pyodide, rendering it in an iframe, and verifying the content is visible.

### Test Artifacts

Tests generate the following artifacts:

- **Screenshots**: `tests/screenshots/` - Contains screenshots of test runs (both passed and failed)
- **Wheel Package**: `dist/imposition-0.1.0-py3-none-any.whl` - Built package for Pyodide

### Troubleshooting

**Test fails with "404 - File not found" for the wheel:**

- Make sure you've built the package first with `python -m build --wheel`

**Test fails with "playwright: command not found":**

- Install Playwright browsers: `python -m playwright install chromium`

**Test times out waiting for iframe:**

- Check that the HTTP server is running properly
- Verify that Pyodide can load from the CDN (requires internet connection)

## Roadmap

For a detailed competitive analysis and the strategic reasoning behind this roadmap, please see [`COMPETITIVE_ANALYSIS.md`](./COMPETITIVE_ANALYSIS.md).

The following is a prioritized roadmap for the `Imposition` library, based on a competitive analysis of existing EPUB libraries.

### Phase 1: Minimum Viable Product (MVP)

1. **Table of Contents:**
    - **Priority:** High
    - **Rationale:** Essential for basic navigation.
2. **Chapter Navigation (Next/Previous):**
    - **Priority:** High
    - **Rationale:** Core functionality for a reading application.
3. **Font Size Adjustment:**
    - **Priority:** Medium
    - **Rationale:** A common and expected feature for readability.

### Phase 2: Core Feature Expansion

1. **Location & Pagination (CFI):**
    - **Priority:** High
    - **Rationale:** Enables saving and restoring the user's position.
2. **Custom Themes (Light/Dark):**
    - **Priority:** Medium
    - **Rationale:** A popular feature for user comfort.
3. **Search (within the book):**
    - **Priority:** Medium
    - **Rationale:** A valuable tool for research and navigation.

### Phase 3: Advanced Features

1. **Annotations (Highlighting & Notes):**
    - **Priority:** High
    - **Rationale:** A key feature for students, researchers, and active readers.
2. **Bookmarks:**
    - **Priority:** Medium
    - **Rationale:** A user-friendly way to save important locations.
3. **Spreads (Two-page view):**
    - **Priority:** Low
    - **Rationale:** A nice-to-have feature, but not essential for a first version.

### Phase 4: Long-Term Vision

1. **Accessibility Features (TTS, Dyslexia Fonts):**
    - **Priority:** High
    - **Rationale:** A key differentiator and a socially responsible goal.
2. **OPDS Catalog Support:**
    - **Priority:** Medium
    - **Rationale:** Enables users to browse and add books from online catalogs.
3. **DRM (LCP) Support:**
    - **Priority:** Low
    - **Rationale:** A complex feature that is only necessary for commercial applications.
