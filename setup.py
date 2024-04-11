"""Setup file for codey-assist"""

from setuptools import setup, find_packages

setup(
    name="codey-assist",  # The name of your package
    version="0.1.0",  # Initial version
    description="A Jupyter Notebook extension for AI-assisted code generation",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),  # Automatically finds your codey_assist package
    install_requires=[
        "jupyter",  # Necessary for any Jupyter extension
        "google-cloud-aiplatform",  # For interaction with Vertex AI
        "langchain",
        "langchain_google_vertexai",
        "chromadb",
    ],
    entry_points={
        "console_scripts": ["codey-assist = codey_assist:load_ipython_extension"]
    },
)
