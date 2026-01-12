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

## Programmatic checks

Currently, there are no programmatic checks. This section can be updated in the future to include any checks that can be run to verify the quality of the code.
