# 🛠️ Developer & Contributing Guide

Thank you for your interest in contributing to **ai-pack**! This guide contains instructions for setting up your development environment, running unit tests, and adhering to our code style guidelines.

---

## 📁 Project Architecture

The codebase follows the modern Python `src/` layout:

```text
ai-pack/
├── src/
│   └── ai_pack/
│       ├── __init__.py      # Package version & top-level re-exports
│       ├── __main__.py      # Module execution entry point (python3 -m ai_pack)
│       ├── cli.py           # CLI argument parsing & main execution flow
│       ├── constants.py     # EXTENSION_MAP & predefined system PROMPTS
│       ├── git.py           # GitHelper & GitignoreMatcher (non-git fallback)
│       ├── packer.py        # Directory walking, file filtering & Markdown packing
│       ├── skeleton.py      # Binary check & SkeletonExtractor (codesigs)
│       ├── ui.py            # Interactive checkbox menu (questionary)
│       └── utils.py         # OSC 52 SSH clipboard helper
├── tests/                   # Unit test suite
├── pyproject.toml           # Package build setup & Ruff linter/formatter config
├── setup.py                 # Setuptools configuration
└── README.md                # User documentation
```

---

## 🚀 Quick Setup for Local Development

### 1. Clone & Setup Environment

```bash
# Clone the repository
git clone https://github.com/iamraydoan/ai-pack.git
cd ai-pack

# Create and activate a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install the package in editable mode
pip install -e .
```

### 2. Install Development & Formatting Tools

We use **Ruff** for linting and code formatting:

```bash
pip install ruff
```

---

## 🧪 Running Unit Tests

Unit tests are written using Python's standard `unittest` framework.

Run all tests from the repository root:

```bash
python3 -m unittest discover tests
```

*Note: Individual test modules can also be run directly:*
```bash
python3 tests/test_binary.py
python3 tests/test_gitignore.py
python3 tests/test_skeleton.py
```

---

## 🎨 Code Style, Linting & Formatting

We strictly enforce **PEP 8** style guidelines and import sorting using [Ruff](https://github.com/astral-sh/ruff).

### 1. Check Linting & Unused Imports

```bash
ruff check .
```

### 2. Auto-Fix Linting Issues

```bash
ruff check --fix .
```

### 3. Format Code

To ensure consistent formatting across all files, run the formatter before submitting a Pull Request:

```bash
ruff format .
```

---

## 🔄 Pull Request Workflow

1. Fork the repository & create your feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Make your code changes in `src/ai_pack/`.
3. Add or update unit tests in `tests/`.
4. Run tests and formatting checks:
   ```bash
   python3 -m unittest discover tests
   ruff check .
   ruff format .
   ```
5. Commit your changes with clear commit messages:
   ```bash
   git commit -m "feat: add support for custom prompt templates"
   ```
6. Push to your branch and open a Pull Request!

---

## 📦 Releasing & Publishing a New Version

To release a new version to PyPI, follow these steps:

### 1. Bump the Version Number

Update the version string (e.g., `0.2.0`) in the following **3 files**:

1. `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```
2. `setup.py`:
   ```python
   version="0.2.0",
   ```
3. `src/ai_pack/__init__.py`:
   ```python
   __version__ = "0.2.0"
   ```

### 2. Commit, Tag, and Push

Commit the version bump and push a new Git version tag matching `v*`:

```bash
# 1. Commit the version bump
git commit -am "chore: bump version to 0.2.0"

# 2. Create a git tag matching the release version (with 'v' prefix)
git tag v0.2.0

# 3. Push main branch and the tag to GitHub
git push origin main
git push origin v0.2.0
```

### 3. Automated PyPI Deployment

Pushing a tag starting with `v*` (e.g. `v0.2.0`) automatically triggers the **GitHub Actions** workflow (`.github/workflows/publish.yml`), which will:
1. Run all unit tests.
2. Build source and wheel packages.
3. Automatically publish the new release to **PyPI** via OIDC Trusted Publishing.
