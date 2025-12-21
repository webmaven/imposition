# Imposition

This is the initial implementation of the `Imposition` library, a Python library intended to run under Pyodide for parsing and rendering EPUB files.

## Current Status

The library can successfully fetch and parse an EPUB file and render the content in an iframe. The project is configured with `hatch` for dependency management and `pytest` for testing.

## Roadmap

For a detailed competitive analysis and the strategic reasoning behind this roadmap, please see [`COMPETITIVE_ANALYSIS.md`](./COMPETITIVE_ANALYSIS.md).

The following is a prioritized roadmap for the `Imposition` library, based on a competitive analysis of existing EPUB libraries.

### Phase 1: Minimum Viable Product (MVP)

1.  **Table of Contents:**
    *   **Priority:** High
    *   **Rationale:** Essential for basic navigation.
2.  **Chapter Navigation (Next/Previous):**
    *   **Priority:** High
    *   **Rationale:** Core functionality for a reading application.
3.  **Font Size Adjustment:**
    *   **Priority:** Medium
    *   **Rationale:** A common and expected feature for readability.

### Phase 2: Core Feature Expansion

4.  **Location & Pagination (CFI):**
    *   **Priority:** High
    *   **Rationale:** Enables saving and restoring the user's position.
5.  **Custom Themes (Light/Dark):**
    *   **Priority:** Medium
    *   **Rationale:** A popular feature for user comfort.
6.  **Search (within the book):**
    *   **Priority:** Medium
    *   **Rationale:** A valuable tool for research and navigation.

### Phase 3: Advanced Features

7.  **Annotations (Highlighting & Notes):**
    *   **Priority:** High
    *   **Rationale:** A key feature for students, researchers, and active readers.
8.  **Bookmarks:**
    *   **Priority:** Medium
    *   **Rationale:** A user-friendly way to save important locations.
9.  **Spreads (Two-page view):**
    *   **Priority:** Low
    *   **Rationale:** A nice-to-have feature, but not essential for a first version.

### Phase 4: Long-Term Vision

10. **Accessibility Features (TTS, Dyslexia Fonts):**
    *   **Priority:** High
    *   **Rationale:** A key differentiator and a socially responsible goal.
11. **OPDS Catalog Support:**
    *   **Priority:** Medium
    *   **Rationale:** Enables users to browse and add books from online catalogs.
12. **DRM (LCP) Support:**
    *   **Priority:** Low
    *   **Rationale:** A complex feature that is only necessary for commercial applications.
