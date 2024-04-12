"""Module to generate code"""

import os
import vertexai
from vertexai.language_models import CodeGenerationModel


def generate_code(prompt, other_code):
    """Function to encapsulate the call to your Vertex AI model."""

    vertexai.init(project=os.environ["PROJECT_ID"], location="us-central1")
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

Do not put the code inside backticks(```) or give any other text. Give the code directly.
Code:"""
    response = model.predict(prefix=input_prompt, **parameters)
    response_text = response.text.replace("```python", "").replace("```", "").strip()
    response_text = "# Generated code\n" + response_text

    return response_text
