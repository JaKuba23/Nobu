# Contributing to Nobu

Thank you for your interest in contributing to Nobu! This document provides guidelines and information for contributors.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. Be kind, constructive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** when available
3. **Include details:**
   - Python version and OS
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages or logs

### Suggesting Features

1. **Open a feature request issue**
2. **Describe the use case** - why is this feature needed?
3. **Propose implementation** if you have ideas

### Submitting Code

#### Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/nobu.git
cd nobu

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```

#### Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Write tests** for new functionality

4. **Run the test suite:**
   ```bash
   pytest
   ```

5. **Run linting:**
   ```bash
   flake8 nobu/
   mypy nobu/
   ```

6. **Format code:**
   ```bash
   black nobu/ tests/
   isort nobu/ tests/
   ```

7. **Commit with a clear message:**
   ```bash
   git commit -m "feat: add UDP scanning support"
   ```

8. **Push and create a pull request**

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 88 characters (Black default)
- Use docstrings for public functions and classes

### Docstring Format

```python
def scan_port(host: str, port: int) -> ScanResult:
    """
    Scan a single port on the target host.
    
    Args:
        host: Target hostname or IP address
        port: Port number to scan (1-65535)
        
    Returns:
        ScanResult containing port state and optional banner
        
    Raises:
        ValueError: If port is out of valid range
    """
```

### Commit Messages

Use conventional commit format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

### Testing

- Write tests for all new functionality
- Maintain or improve code coverage
- Use descriptive test names
- Test edge cases and error conditions

## Project Structure

```
nobu/
├── nobu/           # Main package
│   ├── cli.py      # Command-line interface
│   ├── scanner.py  # Core scanning logic
│   ├── output.py   # Output formatting
│   └── utils.py    # Utility functions
├── tests/          # Test suite
└── examples/       # Usage examples
```

## Review Process

1. All submissions require review before merging
2. Maintainers may request changes or clarifications
3. CI checks must pass (tests, linting, type checking)
4. At least one approving review is required

## Questions?

Open an issue with the "question" label or reach out to the maintainers.

---

Thank you for contributing to Nobu!

