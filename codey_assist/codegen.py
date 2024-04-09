import logging

import vertexai
from vertexai.language_models import CodeGenerationModel


def generate_code(prompt, other_code, logger=None):
    """Function to encapsulate the call to your Vertex AI model."""

    logger = logger or logging.getLogger(__name__)

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
    logger.info(f"Input prompt: {input_prompt}")

    response = model.predict(prefix=input_prompt, **parameters)

    return response.text
