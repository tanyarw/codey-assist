"""Setup file for codey-assist"""

from setuptools import setup, find_packages

setup(
    name="codey-assist",
    version="0.1.0",
    description="A Jupyter Notebook extension for AI-assisted code generation and development.",
    author="Tanya Warrier, Harsh Anand",
    author_email="tanyawarrier@google.com, hrshanand@google.com",
    packages=find_packages(),
    install_requires=[
        "jupyter",
        "google-cloud-aiplatform",
        "langchain",
        "langchain_google_vertexai",
        "chromadb",
    ],
    entry_points={
        "console_scripts": ["codey-assist = codey_assist:load_ipython_extension"]
    },
)
