import vertexai
from vertexai.language_models import CodeGenerationModel


def generate_code(prompt, code_context):
    """Function to encapsulate the call to your Vertex AI model."""

    vertexai.init(project="gdc-ai-playground", location="us-central1")
    model = CodeGenerationModel("code-bison@002")
    response = model.predict("\n".join(code_context) + "\n" + prompt)

    return response.text
