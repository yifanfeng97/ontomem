# Contributing

We welcome contributions to Ontomem! Here's how to get started.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yifanfeng97/ontomem.git
cd ontomem

# Install development dependencies
uv sync --group dev
```

## Making Changes

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest tests/`
4. Format code: `black .`
5. Commit: `git commit -m "Add feature description"`
6. Push: `git push origin feature/your-feature`
7. Create a Pull Request

## Code Style

- Use `black` for formatting
- Use `ruff` for linting
- Follow PEP 8
- Add docstrings to functions

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_core.py

# Run with coverage
pytest --cov=ontomem tests/
```

## Documentation

- Update docstrings for new features
- Update README if adding new capabilities
- Build docs: `mkdocs serve`

## Issues & Discussions

- **Bug reports**: [GitHub Issues](https://github.com/yifanfeng97/ontomem/issues)
- **Feature requests**: [GitHub Issues](https://github.com/yifanfeng97/ontomem/issues)
- **Questions**: [GitHub Discussions](https://github.com/yifanfeng97/ontomem/discussions)

---

Thank you for contributing! 🚀
