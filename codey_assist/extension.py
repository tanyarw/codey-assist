"""Extension for the magic commands."""

import os
from IPython.core.magic import line_magic, cell_magic, Magics, magics_class
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.vectorstores.chroma import Chroma

from codey_assist import codegen, code_qna_gen


@magics_class
class CodeyMagic(Magics):
    """Class for the magic commands."""

    def __init__(self, shell):
        super().__init__(shell)  # Initialize the parent class
        self.shell = shell  # Store the IPython instance
        self.persist_path = "codey_assist.index"

    @cell_magic
    def codey(self, line, cell):
        """Handler for the %%codey magic command."""

        # Fetch code cells
        code_cells = []
        for input_cell in self.shell.user_ns["In"]:

            # Ignore code cells that use %%codey or %load_ext magic commands
            if not input_cell.startswith("get_ipython().run_cell_magic('codey'"):
                if (
                    "get_ipython().run_line_magic('load_ext', 'codey_assist'"
                    in input_cell
                ):
                    input_cell = input_cell.replace(
                        "get_ipython().run_line_magic('load_ext', 'codey_assist')", ""
                    )
                if "get_ipython().run_line_magic('index', ''" in input_cell:
                    input_cell = input_cell.replace(
                        "get_ipython().run_line_magic('index', '')", ""
                    )
                code_cells.append(input_cell)

        other_code = "\n".join(code_cells)

        # Generate code by passing historical code cells in the prompt
        generated_code = codegen.generate_code(line + "\n" + cell, other_code)

        # Add response to the next cell
        print("Check out the next cell!")
        self.shell.set_next_input(generated_code, replace=False)

    @line_magic
    def index(self, line):
        """Handler for the %index magic command."""
        self.persist_path = os.path.join(line, self.persist_path)

        # Find files in the current working directory and sub-directories
        all_files = []

        for root, _, files in os.walk(line):

            # TODO: Read from .gitignore
            # Ignore some folders
            ignore_patterns = [
                ".venv",
                "__pycache__",
                ".vscode",
                ".idea",
                ".git",
                "build",
                ".ipynb_checkpoints",
                "codey_assist",
            ]
            if any(pattern in root for pattern in ignore_patterns):
                continue

            # Find all other files
            for name in files:
                print(name)
                relative_path = os.path.relpath(os.path.join(root, name))
                all_files.append(relative_path)

        # Split code into chunks
        code_chunks = []
        for file in all_files:
            code_chunks.extend(code_qna_gen.chunk_code(file))

        # Create Chroma DB index with chunked code
        code_qna_gen.create_index(code_chunks, persist_path=self.persist_path)

    @cell_magic
    def code_qna(self, line, cell):
        """Handler for the %%code_qna magic command."""

        embeddings = VertexAIEmbeddings(
            model_name="textembedding-gecko@003",
        )

        # Load index
        db = Chroma(persist_directory=self.persist_path, embedding_function=embeddings)

        # Retrieve relevant code chunks and generate a response
        answer = code_qna_gen.answer_question(line + "\n" + cell, db)

        print(answer)
