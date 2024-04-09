import logging

from .codegen import generate_code
from .extension import CodeyMagic

def load_jupyter_server_extension(ipython):
    """Called when the extension is loaded."""

    logger = logging.getLogger('codey-assist')  # Get a logger for your extension
    logger.setLevel(logging.INFO)  # Set the desired logging level

    # Create a basic console handler
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    magic = CodeyMagic(ipython, logger)
    ipython.register_magics(magic)
