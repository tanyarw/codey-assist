"""Codey Magic init"""

from .codegen import generate_code
from .code_qna_gen import create_index, answer_question
from .utilities import changed_files, chunk_code
from .extension import CodeyMagic

def load_ipython_extension(ipython):
    """Called when the extension is loaded."""

    # Create a basic console handler

    magic = CodeyMagic(ipython)
    ipython.register_magics(magic)
