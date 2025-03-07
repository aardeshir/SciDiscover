from setuptools import setup, find_packages

setup(
    name="scidiscover",
    version="0.2.0",
    description="A scientific discovery framework for analyzing molecular mechanisms and pathways",
    author="ArdeshirLab",
    author_email="contact@ardeshirlab.org",
    url="https://github.com/ArdeshirLab/scidiscover",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.51.0",
        "networkx>=3.4.2",
        "openai>=1.65.2",
        "pandas>=2.2.3",
        "plotly>=6.0.0",
        "streamlit>=1.42.2",
        "numpy>=1.26.0",
        "graphviz>=0.20.1",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)