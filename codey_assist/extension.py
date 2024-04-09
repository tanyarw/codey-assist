import logging
from IPython.core.magic import (cell_magic, Magics, magics_class)

from codey_assist import codegen

@magics_class
class CodeyMagic(Magics):
    def __init__(self, shell, logger=None):
        super().__init__(shell)  # Initialize the parent class
        self.shell = shell  # Store the IPython instance
        self.logger = logger or logging.getLogger(__name__)  # Get a logger for your extension

    @cell_magic
    def codey(self, _, cell):
        """Handler for the %codey magic command."""

        self.logger.info(f"Magic command query: {cell}")

        # Fetch code cells
        code_cells = []
        for input_cell in self.shell.user_ns['In']:
            if not input_cell.startswith("get_ipython().run_cell_magic('codey'"):
              if "get_ipython().run_line_magic('load_ext', 'codey_assist'" in input_cell:
                  input_cell = input_cell.replace("get_ipython().run_line_magic('load_ext', 'codey_assist')", "")
              code_cells.append(input_cell)

        other_code = "\n".join(code_cells)
        self.logger.info(f"Other code cells found: {other_code}")

        generated_code = codegen.generate_code(cell, other_code)
        self.logger.info(f"Generated: {generated_code}")

        # # Replace *only* the existing code content:
        # existing_lines = cell.splitlines(keepends=True)  # Get each line of the cell

        # # (Logic to find where your existing code is within the cell - this is a placeholder!)
        # start_index = 0  # You'll likely need to analyze existing_lines for markers
        # end_index = len(existing_lines)  # Replace everything until the end

        # new_lines = existing_lines[:start_index] + [generated_code] + existing_lines[end_index:]
        # new_cell_content = "".join(new_lines)

        # # Replace the cell content
        # self.shell.run_cell(new_cell_content)
