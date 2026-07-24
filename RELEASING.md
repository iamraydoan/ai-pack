# 📦 Maintainer Release Guide (`RELEASING.md`)

This guide is intended for **Repository Owners and Maintainers** with write access to `ai-pack`. It details the step-by-step process for bumping version numbers, creating Git tags, and deploying releases to PyPI.

---

## 🚀 Step-by-Step Release Process

### 1. Bump Version Number in 3 Files

Update the version string (e.g. `0.2.0`) across the following files:

1. **`pyproject.toml`**:
   ```toml
   version = "0.2.0"
   ```
2. **`setup.py`**:
   ```python
   version="0.2.0",
   ```
3. **`src/ai_pack/__init__.py`**:
   ```python
   __version__ = "0.2.0"
   ```

---

### 2. Commit, Tag, and Push

Commit the version bump and push a new Git version tag matching `v*`:

```bash
# 1. Stage and commit the version bump
git commit -am "chore: bump version to 0.2.0"

# 2. Create a git tag matching the release version (with 'v' prefix)
git tag v0.2.0

# 3. Push the main branch and the tag to GitHub
git push origin main
git push origin v0.2.0
```

---

### 3. Automated PyPI Deployment

Pushing a tag starting with `v*` (e.g. `v0.2.0`) automatically triggers the **GitHub Actions** workflow ([`.github/workflows/publish.yml`](.github/workflows/publish.yml)), which will:

1. Run the full unit test suite.
2. Build source (`sdist`) and wheel (`bdist_wheel`) packages.
3. Publish the release to **PyPI** via OIDC Trusted Publishing.
