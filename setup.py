from setuptools import setup

# Read the contents of README.md to use as the long description on PyPI
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-pack-cli",
    version="0.1.1",
    py_modules=["ai_pack"],
    install_requires=[
        "pyperclip>=1.8.2",
        "questionary>=1.10.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-pack=ai_pack:main",
            "aipack=ai_pack:main",
            "aip=ai_pack:main",
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
