from setuptools import setup, find_packages

setup(
    name="promptvault",
    version="1.1.0",
    description="Local GUI Prompt Manager",
    author="Milo",
    author_email="milo@example.com",
    url="https://github.com/milolywood-cmd/promptvault",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.5.0",
    ],
    entry_points={
        "console_scripts": [
            "promptvault=main:main",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)