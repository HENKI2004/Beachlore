## Description
Provide a brief summary of the changes and the motivation behind them. If this PR fixes a bug, please link the issue here (e.g., "Fixes #123").

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update (changes to docs or docstrings)

## Checklist
*Before submitting this PR, please ensure:*
- [ ] **Code Quality:** I have run `ruff format .` and `ruff check .` to maintain code standards.
- [ ] **Testing:** I have tested these changes locally (e.g., via `pytest` or manual execution of `main.py`).
- [ ] **Safety Logic:** Any changes to FIT rate calculations or logic blocks (`core/`) follow ISO 26262 principles.
- [ ] **Visualization:** If I modified hardware blocks, I have verified that `generate_pdf()` still produces correct Graphviz diagrams.
- [ ] **Documentation:** I have updated the `README.md`, docstrings, or `docs/` if necessary.

## Screenshots (if applicable)
If this PR changes the architectural visualization, please attach a screenshot of the generated PDF report.

## Additional Notes
Add any other information about this PR here.