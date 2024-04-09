import re

def extract_code(cell):
    """Extracts code blocks from a Jupyter cell."""
    code_blocks = []
    code_pattern = r"`(.*?)`"  # Regex for fenced code blocks
    code_matches = re.findall(code_pattern, cell, flags=re.DOTALL)

    if code_matches:
        code_blocks = list(code_matches)

    return code_blocks

def extract_markdown(cell):
    """Extracts Markdown text from a Jupyter cell."""
    markdown_text = ""
    code_pattern = r"`(.*?)`"  # Regex for fenced code blocks
    code_removed = re.sub(code_pattern, '', cell)  # Remove code blocks

    # Basic cleanup (you can make this more sophisticated later)
    markdown_text = code_removed.strip()

    return markdown_text
