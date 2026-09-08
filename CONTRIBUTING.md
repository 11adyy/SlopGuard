# Contributing to SlopGuard

Thank you for your interest in contributing to SlopGuard! We welcome contributions from the community to help improve AI detection and prevent slop from cluttering our repositories.

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip or poetry for dependency management

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/SlopGuard.git
   cd SlopGuard
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

Before submitting a pull request, ensure all tests pass:

```bash
python -m pytest -q
```

### Code Quality Checks

We use multiple tools to maintain code quality:

**Ruff (Linting and Formatting):**
```bash
python -m ruff check .
python -m ruff format .
```

**Type Checking:**
```bash
python -m mypy src/slopguard main.py
```

**Run all checks at once:**
```bash
python -m pytest -q && python -m ruff check . && python -m mypy src/slopguard main.py
```

## Submitting Changes

### Branch Naming

Use clear, descriptive branch names:
- `feature/add-new-detection-model` for new features
- `fix/resolve-false-positives` for bug fixes
- `docs/improve-readme` for documentation
- `refactor/simplify-detection-logic` for refactoring

### Commit Messages

Write clear, concise commit messages:
- Use the imperative mood ("add feature" not "added feature")
- Keep the first line under 72 characters
- Include relevant issue numbers (e.g., "Closes #123")

Example:
```
Add ML model for detecting GPT-generated content

Implement transformer-based model for improved detection accuracy.
Closes #42
```

### Pull Request Guidelines

1. **Before creating a PR:**
   - Ensure all tests pass
   - Run linting and type checking
   - Update documentation if needed
   - Add tests for new features

2. **PR Description should include:**
   - Clear title describing the change
   - Why this change is needed
   - How it was implemented
   - Any breaking changes
   - Screenshots/examples if applicable

3. **PR checklist:**
   - [ ] Tests pass locally
   - [ ] Ruff checks pass
   - [ ] Type checking passes
   - [ ] Documentation updated
   - [ ] No unnecessary dependencies added

## Code Style

### Python Style Guide

- Follow PEP 8 guidelines
- Use type hints for all functions
- Keep functions focused and single-purpose
- Maximum line length: 100 characters (enforced by Ruff)

### Naming Conventions

- `snake_case` for variables and functions
- `PascalCase` for classes
- `UPPER_CASE` for constants

### Example:

```python
from typing import Optional

class AIDetector:
    """Detects AI-generated content."""
    
    DEFAULT_THRESHOLD: float = 0.75
    
    def detect_slop(self, text: str) -> Optional[dict]:
        """
        Detect if text is AI-generated.
        
        Args:
            text: The text to analyze
            
        Returns:
            Detection result or None if no detection
        """
        confidence = self._calculate_confidence(text)
        return {"is_slop": confidence > self.DEFAULT_THRESHOLD}
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score for text."""
        pass
```

## Testing

### Writing Tests

- Use `pytest` framework
- Place tests in the `tests/` directory
- Use descriptive test names: `test_detects_gpt_generated_content`
- Aim for >80% code coverage

Example test:

```python
import pytest
from slopguard.detector import AIDetector

def test_detects_obvious_slop():
    """Test that obvious AI content is detected."""
    detector = AIDetector()
    text = "This is clearly AI-generated slop content..."
    result = detector.detect_slop(text)
    assert result is not None
    assert result["is_slop"] is True
```

## Documentation

- Keep README.md up to date
- Document public APIs with docstrings
- Use clear, concise language
- Include examples where helpful

## Issues and Discussions

- Check existing issues before creating duplicates
- Provide minimal reproducible examples for bugs
- Be respectful and constructive in discussions
- Use GitHub discussions for feature proposals

## License

By contributing to SlopGuard, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue or reach out to the maintainers. We're here to help!

---

Thank you for contributing to SlopGuard! 🛡️
