"""Module to generate code"""

import vertexai
from vertexai.language_models import CodeGenerationModel


def generate_code(prompt, other_code):
    """Function to encapsulate the call to your Vertex AI model."""

    vertexai.init(project="gdc-ai-playground", location="us-central1")
    parameters = {
      "candidate_count": 1,
      "max_output_tokens": 1024,
      "temperature": 0.5
    }
    model = CodeGenerationModel.from_pretrained("code-bison")
    input_prompt = f"""
You are a python developer working in a jupyter notebook. The code developed in the cells above is as follows:
{other_code}

You have to generate code for the following query.
{prompt}

Surround the code in backticks ```python....```

Code:
    """
    response = model.predict(prefix=input_prompt, **parameters)

    return response.text
