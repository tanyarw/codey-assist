import logging
from IPython.core.magic import (cell_magic, Magics, magics_class)
from IPython import get_ipython

from codey_assist import cell_handlers, codegen

@magics_class
class CodeyMagic(Magics):
    def __init__(self, shell, logger=None):
        super().__init__(shell)  # Initialize the parent class
        self.shell = shell  # Store the IPython instance
        self.logger = logger or logging.getLogger(__name__)  # Get a logger for your extension

    @cell_magic
    def codey(self, line, cell):
        """Handler for the %codey magic command."""
        prompt = line  # For now, take the entire line after %codey as the prompt
        code_blocks = cell_handlers.extract_code(cell)
        self.logger.info(f"Code generation triggered with prompt: {prompt}")

        generated_code = codegen.generate_code(prompt, code_blocks)
        print(generated_code)
        self.logger.info(f"Generated: {generated_code}")

        # Replace *only* the existing code content:
        existing_lines = cell.splitlines(keepends=True)  # Get each line of the cell

        # (Logic to find where your existing code is within the cell - this is a placeholder!)
        start_index = 0  # You'll likely need to analyze existing_lines for markers
        end_index = len(existing_lines)  # Replace everything until the end

        new_lines = existing_lines[:start_index] + [generated_code] + existing_lines[end_index:]
        new_cell_content = "".join(new_lines)

        # Replace the cell content
        self.shell.run_cell(new_cell_content)
