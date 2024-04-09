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
        "requests",  # Example, if you make API calls
        "google-cloud-aiplatform"  # For interaction with Vertex AI
        # Add any other libraries your extension depends on
    ],
    entry_points={
        'console_scripts': [
            'codey-assist = codey_assist.extension:load_jupyter_server_extension'
        ]
    }
)
