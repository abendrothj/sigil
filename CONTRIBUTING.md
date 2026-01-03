# Contributing to Sigil

Thank you for your interest in contributing to Sigil! This document provides guidelines and information for contributors.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [CI/CD Pipeline](#cicd-pipeline)

## Code of Conduct

This project adheres to professional and respectful collaboration standards. Please be considerate and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/sigil.git
   cd sigil
   ```
3. **Set up the development environment**:
   ```bash
   ./setup.sh
   source venv/bin/activate
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Making Changes

1. Make your changes in your feature branch
2. Add tests for any new functionality
3. Ensure all tests pass locally:
   ```bash
   ./run_tests.sh
   ```
4. Commit your changes with descriptive messages
5. Push to your fork and create a pull request

### Running Tests Locally

```bash
# Run all tests
./run_tests.sh

# Run with verbose output
./run_tests.sh verbose

# Run with coverage
./run_tests.sh coverage

# Run specific test categories
./run_tests.sh unit
./run_tests.sh api
./run_tests.sh cli
```

### Running the API Locally

```bash
./run_api.sh
```

### Running the Web UI Locally

```bash
./run_web.sh
```

## Testing

- All new features must include appropriate tests
- Aim for high code coverage (>80%)
- Tests should be fast and deterministic
- Use pytest fixtures for common test setup
- Mock external dependencies appropriately

### Test Structure

```
tests/
├── test_crypto_signatures.py   # Cryptographic signature tests
├── test_api.py                 # API endpoint tests
├── test_cli.py                 # CLI command tests
└── experimental/               # Experimental tests
```

## Code Style

We use automated tools to maintain code quality:

### Python Style Guide

- Follow PEP 8 conventions
- Line length: 100 characters maximum
- Use type hints where appropriate
- Write docstrings for public functions/classes

### Linting Tools

The CI pipeline automatically checks:

- **Ruff**: Fast Python linter
- **Black**: Code formatter (informational)
- **isort**: Import sorting (informational)

Run locally:
```bash
# Check with Ruff
pip install ruff
ruff check .

# Format with Black
pip install black
black .

# Sort imports
pip install isort
isort .
```

Configuration is in `pyproject.toml`.

## Commit Messages

Use clear, descriptive commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(cli): add batch processing support

Implements batch video processing for the extract command.
Processes multiple videos in parallel using multiprocessing.

Closes #42
```

```
fix(api): resolve signature verification timeout

Increases timeout for Ed25519 signature verification
from 5s to 30s for large video files.

Fixes #87
```

## Pull Request Process

1. **Update documentation** if you're adding/changing functionality
2. **Add tests** for new features
3. **Ensure CI passes** - all checks must be green
4. **Update CHANGELOG.md** if applicable
5. **Request review** from maintainers
6. **Address feedback** promptly and professionally
7. **Squash commits** if requested before merging

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] No merge conflicts
- [ ] CI pipeline passes

## CI/CD Pipeline

Our GitHub Actions pipeline runs automatically on every push and pull request.

### CI Workflow

The CI pipeline includes:

1. **Test Suite** (Python 3.8, 3.9, 3.10, 3.11)
   - Installs dependencies
   - Runs pytest with coverage
   - Uploads coverage to Codecov

2. **Code Quality**
   - Ruff linting
   - Black formatting check
   - isort import sorting check

3. **Docker Build**
   - Builds API Docker image
   - Builds Web UI Docker image
   - Validates docker-compose config

4. **Security Scan**
   - Safety check for vulnerable dependencies
   - Bandit security scan

### Viewing CI Results

- Check the **Actions** tab in the GitHub repository
- All checks must pass before merging
- Click on failed checks to see detailed logs
- Re-run failed jobs if needed

### Release Workflow

Releases are automated:

1. Create a tag: `git tag v1.0.0`
2. Push the tag: `git push origin v1.0.0`
3. GitHub Actions automatically:
   - Creates a GitHub Release
   - Generates changelog
   - Builds and publishes Docker images to GHCR

## Project Structure

```
sigil/
├── api/              # Flask API server
├── cli/              # Command-line interface
├── core/             # Core perceptual hash & crypto logic
├── tests/            # Test suite
├── docs/             # Documentation
├── docker/           # Docker configurations
├── experiments/      # Research experiments
└── web-ui/           # Web interface
```

## Questions?

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Tag maintainers if you need help: @abendrothj

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Sigil! 🎉
