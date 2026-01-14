# AGENTS.md

This document provides guidance for AI agents working on the `imposition` codebase.

## About this project

`imposition` is a Python library for parsing and rendering EPUB files. It is designed to run in the browser using [Pyodide](https://pyodide.org/).

## High-level technical strategy

This project prioritizes Python over JavaScript. The goal is to implement as much of the logic as possible in Python, using JavaScript only as a thin layer for interacting with the browser.

When working on this project, you should:

-   **Prefer Python**: Implement new features and fix bugs in Python whenever possible.
-   **Avoid JavaScript**: Do not add new JavaScript or TypeScript dependencies.

## Project priorities

The project's roadmap is outlined in the `README.md` file. However, for day-to-day development, the [GitHub issue tracker](https://github.com/webmaven/imposition/issues/) is the primary source of truth.

-   **Issue tracker > Roadmap**: The issue tracker is more tactical and pragmatic and takes precedence over the roadmap, which is more strategic and aspirational.

## Documentation

### CONTRIBUTING.md

The [`CONTRIBUTING.md`](./CONTRIBUTING.md) file contains instructions for setting up the development environment, running tests, and submitting pull requests. If you make changes to the development process, build steps, or quality checks, you must update this file accordingly.

### CHANGELOG.md

The [`CHANGELOG.md`](./CHANGELOG.md) file tracks the project's version history. For any user-visible changes, such as new features, bug fixes, or performance improvements, you must add an entry to the "Unreleased" section of this file.

## Programmatic checks

To ensure code quality, the following checks are in place. These should be run before submitting any changes.

-   **Tests**: Run the test suite with `hatch run pytest`.
-   **Linting**: Check the code for style issues with `hatch run ruff check .`.
-   **Type Checking**: Verify the type hints with `hatch run mypy .`.
