# Architecture

This document outlines the architecture of the Imposition project, with a focus on its testing strategy. The project runs in two distinct environments: the browser (via Pyodide) and a local Python environment for integration testing. This dual-environment nature presents unique challenges, which are addressed by the testing architecture described below.

## Testing Strategy

The project employs a two-pronged testing strategy to ensure correctness in both its target browser environment and its local development environment.

### End-to-End Tests

End-to-end (E2E) tests are the most critical, as they validate the application's functionality in a real browser environment. These tests use the following tools:

-   **Pytest:** The core testing framework.
-   **Playwright:** For browser automation and interaction.
-   **pytest-playwright:** To integrate Playwright with Pytest.

E2E tests are located in the `tests/` directory and are run as part of the main test suite.

### Integration Tests

Integration tests validate the core application logic in a local Python environment. These tests mock the browser's `js` and `pyodide` APIs, allowing for rapid testing without the overhead of a full browser environment. These tests use the following tools:

-   **Pytest:** The core testing framework.
-   **pytest-asyncio:** To run and manage `async` test functions.

## The Event Loop Conflict

A significant challenge in this project is the event loop conflict between `pytest-asyncio` and `pytest-playwright`. Both libraries attempt to manage the `asyncio` event loop, leading to a `RuntimeError: Cannot run the event loop while another loop is running` when they are used in the same test suite.

### The Solution: Test Suite Isolation

The conflict is resolved by isolating the integration tests into their own, separate test suite. This is achieved through the following steps:

1.  **Dedicated Directory:** The integration tests are moved to a `tests/integration` directory.
2.  **Dedicated `pytest.ini`:** This directory contains its own `pytest.ini` file, which enables `asyncio_mode = auto` for the integration tests.
3.  **Dedicated `conftest.py`:** The `tests/integration` directory also contains a `conftest.py` file to mock the necessary browser-specific modules (`js`, `pyodide`, etc.).
4.  **Root `pytest.ini` Exclusion:** The root `pytest.ini` is configured to ignore the `tests/integration` directory, ensuring that the two test suites are run independently.

## CI/CD Configuration

The CI/CD pipeline, defined in `.github/workflows/ci.yml`, is configured to run both test suites and ensure all dependencies are correctly installed. Key dependencies include:

-   `playwright` and `pytest-playwright`: For the E2E tests.
-   `nest-asyncio`: To handle nested event loops, which can be an issue with Playwright.
-   **Playwright Browsers:** The CI workflow includes a dedicated step to run `playwright install`, which downloads the necessary browser binaries.

## Key Learnings and Best Practices

-   **Build Before Testing:** The project's Python wheel must be built with `hatch build` before running the E2E tests, as the browser-based tests rely on this wheel.
-   **Isolate Conflicting Dependencies:** When two dependencies conflict (like `pytest-asyncio` and `pytest-playwright`), isolating them into separate test suites is a robust solution.
-   **Comprehensive CI:** The CI pipeline must install *all* dependencies, including browser binaries, to ensure a reliable testing environment.
-   **Type Safety:** `mypy` is used for static type checking. When working with external libraries or APIs that may return `None`, it is crucial to add assertions or explicit checks to ensure type safety.
