from .codegen import generate_code
from .code_qna_gen import chunk_code, create_index, answer_question
from .extension import CodeyMagic

def load_ipython_extension(ipython):
    """Called when the extension is loaded."""

    # Create a basic console handler

    magic = CodeyMagic(ipython)
    ipython.register_magics(magic)
