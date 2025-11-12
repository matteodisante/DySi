# GitHub Actions Workflows

## Disabled Workflows

### docs.yml.disabled
**Reason**: Sphinx documentation setup was removed in favor of Markdown documentation.

The project now uses:
- Markdown files in `docs/` directory
- Simple GitHub Pages deployment (if needed)
- No build process required

If documentation deployment is needed in the future, consider:
1. **GitHub Pages with Markdown**: Direct deployment of `docs/` folder
2. **MkDocs**: Modern documentation framework with minimal setup
3. **Docusaurus**: React-based documentation site

---

## Active Workflows

Currently no active GitHub Actions workflows.

### Potential Future Workflows
- **Tests**: Run pytest on push/PR
- **Linting**: Black, flake8, mypy checks
- **Release**: Automated versioning and changelog
