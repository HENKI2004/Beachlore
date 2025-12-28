# Contributing to iso26262-ecc-analyzer

First off, thank you for considering contributing to the **iso26262-ecc-analyzer** project! It is contributions like yours that make open-source tools better for the safety community.

## Code of Conduct
By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs
If you find a bug (such as an incorrect FIT rate calculation or a visualization error), please use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md). Provide as much detail as possible, including your environment and steps to reproduce the issue.

### Suggesting Enhancements
We welcome ideas for new hardware blocks, safety metrics, or visualization improvements. Please use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Pull Requests
Small fixes or documentation updates can be submitted via Pull Requests. For larger changes, please open an issue first to discuss your proposal.

## Development Setup

To set up your local development environment, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/HENKI2004/iso26262-ecc-analyzer.git](https://github.com/HENKI2004/iso26262-ecc-analyzer.git)
   cd iso26262-ecc-analyzer
   ```
2. **Install in editable mode with development dependencies: This project requires Python 3.9+ and uses pytest, black, and ruff for development.**
   ```bash
   pip install -e .[dev]
   ```
3. **Install Graphviz: Ensure Graphviz is installed on your system for architectural visualization.**

## Style Guidelines

### Coding Standards

We use Ruff for linting and formatting to maintain high code quality. Before submitting a PR, please run:

```bash
ruff format .
ruff check .
```

### Docstrings

Please follow the Google Python Style Guide for docstrings to ensure compatibility with our documentation generator.

### Testing 

We use pytest for unit testing. Please ensure that your changes do not break existing functionality and, if possible, add new tests for your features.
```bash
pytest
```

## Pull Request Process

1. **Use the Pull Request Template to describe your changes.**

2. **Ensure your code passes all linting and formatting checks.**

3. **Link your PR to any relevant issues.**

4. **Once submitted, your PR will be reviewed as soon as possible.**



