# 📦 ai-pack

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/ai-pack-cli.svg)](https://badge.fury.io/py/ai-pack-cli)
[![GitHub Stars](https://img.shields.io/github/stars/iamraydoan/ai-pack.svg?style=social)](https://github.com/iamraydoan/ai-pack)

Pack your entire codebase, specific files, or uncommitted changes into a single token-optimized Markdown prompt for LLMs (like ChatGPT, Claude, Gemini).

---

> [!IMPORTANT]
> **📋 Default Clipboard Behavior**
>
> By default, running `aip` **automatically copies** the generated Markdown payload directly to your **system clipboard**. No files are saved to disk unless you specify the output file using the `-o` or `--output` flag.
>
> *Note: It also natively supports remote SSH sessions using the OSC 52 clipboard escape sequence.*

---

## ⚡ Key Features

*   **📋 Clipboard-First**: Automatically copies your prompt, ready to paste straight into ChatGPT, Claude, Gemini, or any LLM interface.
*   **💀 Skeleton Mode (`-s` / `--skeleton`)**: Drastically saves tokens by stripping function/method bodies, keeping only class structures, signatures, and imports.
*   **🎯 Interactive Selector (`-i`)**: Choose files interactively via checkbox CLI menu.
*   **🌿 Git-Aware (`-c` / `--changed`)**: Automatically pack only modified, staged, or untracked files.
*   **🛡️ Gitignore-Respecting**: Excludes ignored, temporary, or build files automatically (using `git ls-files` with manual fallback for non-git folders).
*   **💬 Prompt Presets (`-p`)**: Instantly prepend pre-configured prompts for code review, bug hunting, or architecture explanations.
*   **📊 Token Estimation**: Heuristic token counting warns you if your payload exceeds your limit (`--max-tokens`).

---

## 🚀 Quick Start

### Installation

Choose your preferred installation method:

```bash
# Option 1: Install official package via pip (Recommended)
pip3 install ai-pack-cli --user

# Option 2: Install via pipx (Isolated environment)
pipx install ai-pack-cli

# Option 3: Install development version directly from GitHub
pip3 install git+https://github.com/iamraydoan/ai-pack.git --user
```

> [!TIP]
> **Skeleton Mode (`-s` / `--skeleton`) for non-Python languages:**
> To extract code skeletons for JavaScript, TypeScript, Go, Rust, Java, C#, C++, PHP, Lua, CSS, Swift, and Kotlin, install `ast-grep` globally:
> ```bash
> npm install -g @ast-grep/cli
> # or: cargo install ast-grep
> ```

---

## 💡 Usage & Common Scenarios

Here are common ways to use `ai-pack` (using commands `aip`, `ai-pack`, or `aipack`):

### 1. Pack codebase & copy to clipboard (Default)
```bash
aip
```

### 2. Pack specific files/folders and save to a file
```bash
aip -f src/main.py tests/ -o output.md
```

### 3. Pack only uncommitted changes with a code review prompt
```bash
aip -c -p review
```

### 4. Pack code skeleton to save context window tokens
```bash
aip -s -p explain
```

### 5. Choose files interactively before packing
```bash
aip -i
```

---

## ⚙️ CLI Flags & Interactions

### Reference

| Flag | Short | Type | Description |
| :--- | :--- | :--- | :--- |
| `--files` | `-f` | Path(s) | Specific files or directories to pack (space-separated). |
| `--changed` | `-c` | Flag | Pack only modified, staged, or untracked Git files. |
| `--interactive` | `-i` | Flag | Select files interactively via a checkbox menu. |
| `--skeleton` | `-s` | Flag | Strip method bodies, leaving only signatures and imports to save tokens. |
| `--prompt` | `-p` | Choices | Prepend preset: `review`, `bug`, or `explain`. |
| `--output` | `-o` | Path | Save output directly to a file instead of copying to clipboard. |
| `--max-tokens` | | Number | Count approximate tokens and warn if the limit is exceeded. |

### 🤝 Combining Flags

You can combine flags to narrow down and customize your payload:

*   **Filter Git changes (`-f` + `-c` / `--changed`)**:
    Only packs files that are *both* modified/uncommitted AND located inside the specified paths.
    ```bash
    aip -c -f src/
    ```
*   **Interactive selection with filter (`-i` + `-f` / `-c`)**:
    Shows only the filtered list (e.g. only changed files) in the interactive checkbox menu instead of the entire repo.
    ```bash
    aip -i -c
    ```
*   **Structure only (`-s` / `--skeleton` + any mode)**:
    Can be appended to any command to extract skeletons instead of full source code for the selected files.
    ```bash
    aip -i -s
    ```
*   **Redirect output (`-o` vs Default)**:
    By default, everything goes to the clipboard. Use `-o filename.md` to save to a file instead.

---

## 💀 Skeleton Mode Example

### Original Code:
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
def fibonacci(n): ...
```

---

## 🤝 Contributing

Contributions are welcome! Please check out the [Developer & Contributing Guide](CONTRIBUTING.md) for local setup, running unit tests, and code formatting guidelines (`ruff`).

1. Fork the repository.
2. Create your feature branch (`git checkout -b feat/amazing-feature`).
3. Commit your changes (`git commit -m 'feat: add amazing feature'`).
4. Push to the branch (`git push origin feat/amazing-feature`).
5. Open a Pull Request.

Give this repository a ⭐ if it helped you pack your code for LLMs!
