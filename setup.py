from setuptools import setup

setup(
    name="ai-pack",
    version="0.1.0",
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
)
