# 📦 ai-pack

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/ai-pack-cli.svg)](https://badge.fury.io/py/ai-pack-cli)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange.svg)](https://github.com/)
[![GitHub Stars](https://img.shields.io/github/stars/iamraydoan/ai-pack.svg?style=social)](https://github.com/iamraydoan/ai-pack)

> Pack your entire codebase into a single formatted Markdown prompt for LLMs, optimized for minimum tokens.

`ai-pack` is a lightweight, high-performance CLI tool designed to help developers package their codebase, specific files, or uncommitted changes into a clean Markdown payload. Easily copy it to the clipboard or save it to a file to feed directly into ChatGPT, Claude, Gemini, or any other LLM.

---

## 🔥 Key Features

*   **⚡ Native CLI Command**: Accessible globally as `ai-pack`, `aipack`, or `aip`.
*   **💀 Code Skeleton Extraction (`--skeleton`)**: Drastically save tokens by stripping method and function bodies, keeping only class structures, imports, signatures, and docstrings.
*   **🎯 Interactive Selection (`-i`)**: Interactively choose which files to pack using Arrow keys and Spacebar before generating the payload.
*   **🌿 Git-Aware (`--changed`)**: Automatically detect and pack only modified, staged, or untracked files.
*   **🛡️ Gitignore Respecting**: Native Git integration using `git ls-files` to automatically ignore build artifacts, node modules, and everything in `.gitignore` (with a clean manual fallback for non-git folders).
*   **💬 Predefined LLM Prompts (`-p`)**: Instantly prepend pre-configured prompts for code review, bug hunting, or architecture explanations.
*   **📊 Token Estimation**: Heuristic token counting warns you if your payload exceeds your limit (`--max-tokens`).

---

## 🚀 Quick Start

### Installation

Choose one of the following methods to get started quickly:

#### Option 1: Install from PyPI (Recommended)
Install the official release from PyPI:
```bash
pip3 install ai-pack-cli --user
```
Or via `pipx` to run in an isolated environment:
```bash
pipx install ai-pack-cli
```

#### Option 2: Install directly from GitHub
Install the latest cutting-edge development version directly:
```bash
pip3 install git+https://github.com/iamraydoan/ai-pack.git --user
```

#### Option 3: Manual Clone (Editable mode)
If you want to modify the source code:
```bash
git clone https://github.com/iamraydoan/ai-pack.git
cd ai-pack
pip3 install -e . --user
```

#### Option 4: Run as a Standalone Script (One-Liner)
Since `ai-pack` is a self-contained single script, you can download it directly:
```bash
curl -o ~/.local/bin/aip https://raw.githubusercontent.com/iamraydoan/ai-pack/main/ai_pack.py && chmod +x ~/.local/bin/aip
```
*(Note: If you run it standalone, you will need to manually run `pip3 install pyperclip questionary` to enable all optional interactive and clipboard features).*

> [!TIP]
> **Optional backend for Skeleton Mode (`--skeleton`)**:
> If you plan to use skeleton extraction for non-Python languages (such as JavaScript, TypeScript, Go, Rust, Java, C#, C++, PHP, Lua, CSS, Swift, and Kotlin), you must install `ast-grep` globally:
> ```bash
> npm install -g @ast-grep/cli
> # or: cargo install ast-grep
> ```


### Usage Examples

#### 1. Pack the entire repository (copied to clipboard)
```bash
aip
```

#### 2. Pack specific files and save to a file
```bash
aip -f src/main.py tests/ -o output.md
```

#### 3. Pack only uncommitted git changes with a code review prompt
```bash
aip --changed -p review
```

#### 4. Extract code skeleton only (drastically saves context window tokens)
```bash
aip --skeleton -p explain
```

#### 5. Interactively choose files to include
```bash
aip -i
```

---

## 💀 Skeleton Mode Demo

### Original Code (`math.py`):
```python
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence
```

### Skeleton Output:
```python
def fibonacci(n):
    ...
```

*Supports Python, JavaScript, TypeScript, Go, Rust, Java, C#, C++, PHP, Lua, CSS, Swift, and Kotlin via codesigs and ast-grep.*

> [!IMPORTANT]
> **Skeleton Mode Dependencies**:
> * **Python >= 3.9**: Required to run the `--skeleton` feature.
> * **ast-grep**: For non-Python languages, the `ast-grep` command-line tool must be installed globally (e.g. via npm: `npm install -g @ast-grep/cli` or cargo: `cargo install ast-grep`).

---

## 🎨 Interactive CLI Checklist

Running `aip -i` triggers a beautiful checkbox prompt:

```text
? Select files to pack (Space to toggle, Enter to confirm):
 ❯ [x] src/main.py
   [x] src/utils.py
   [ ] tests/test_main.py
```

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features, bug fixes, or enhancements:

1. Fork the repo.
2. Create your feature branch (`git checkout -b feat/amazing-feature`).
3. Commit your changes (`git commit -m 'feat: add amazing feature'`).
4. Push to the branch (`git push origin feat/amazing-feature`).
5. Open a Pull Request.

**Don't forget to give the project a ⭐ if you found it useful!**
