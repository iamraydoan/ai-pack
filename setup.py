from setuptools import find_packages, setup

# Read the contents of README.md to use as the long description on PyPI
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-pack-cli",
    version="0.2.2",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pyperclip>=1.8.2",
        "questionary>=1.10.0",
        "tree-sitter~=0.21.3",
        "tree-sitter-languages~=1.10.2",
    ],
    entry_points={
        "console_scripts": [
            "ai-pack=ai_pack.cli:main",
            "aipack=ai_pack.cli:main",
            "aip=ai_pack.cli:main",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamraydoan/ai-pack",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
