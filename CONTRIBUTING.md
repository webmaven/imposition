# Contributing to Imposition

First off, thank you for considering contributing to Imposition! It's people like you that make open source such a great community.

We welcome contributions of all kinds, from bug reports and feature requests to code and documentation.

## How to Contribute

### Reporting Bugs

If you find a bug, please [open an issue](https://github.com/webmaven/imposition/issues) on our GitHub issue tracker. Please provide a clear and descriptive title, a detailed description of the problem, and steps to reproduce the bug.

### Suggesting Enhancements

If you have an idea for an enhancement, please [open an issue](https://github.com/webmaven/imposition/issues) to discuss it. We're always open to new ideas!

### Pull Requests

If you'd like to contribute code, please follow these steps:

1.  Fork the repository and create a new branch for your feature or bug fix.
2.  Set up your development environment (see below).
3.  Make your changes, and be sure to add or update tests as appropriate.
4.  Ensure that all tests, linting, and type checks pass.
5.  Open a pull request with a clear description of your changes.

## Development Setup

This project uses [Hatch](https://hatch.pypa.io/latest/) to manage dependencies and virtual environments.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/webmaven/imposition.git
    cd imposition
    ```

2.  **Create the development environment:**
    ```bash
    hatch env create
    ```

3.  **Activate the virtual environment:**
    ```bash
    hatch shell
    ```

## Building the Package

To build the wheel for use with Pyodide:

```bash
hatch build
```

This will create a `dist` directory containing the wheel file.

## Quality Checks

Before submitting a pull request, please ensure that your changes pass all of our quality checks. The package must be built before running the tests, as the end-to-end tests require the built wheel.

### Running Tests

This project uses [pytest](https://pytest.org/) for testing. To run the test suite:

```bash
hatch run pytest
```

To run the tests with coverage reporting:

```bash
hatch run pytest --cov=src/imposition
```

### Linting

This project uses [Ruff](https://beta.ruff.rs/docs/) for code linting. To run the linter:

```bash
hatch run ruff check .
```

### Type Checking

This project uses [mypy](http://mypy-lang.org/) for static type checking. To run the type checker:

```bash
hatch run mypy .
```
