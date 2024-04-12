"""Extension for the magic commands."""

import os
from IPython.core.magic import line_magic, cell_magic, Magics, magics_class
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.vectorstores.chroma import Chroma

from codey_assist import codegen, code_qna_gen

@magics_class
class CodeyMagic(Magics):
    """Class for the magic commands."""
    PERSIST_DIR = "codey_assist.index"

    def __init__(self, shell):
        super().__init__(shell)  # Initialize the parent class
        self.shell = shell  # Store the IPython instance

    @cell_magic
    def codey(self, line, cell):
        """Handler for the %%codey magic command."""

        # Fetch code cells
        code_cells = []
        for input_cell in self.shell.user_ns['In']:
            if not input_cell.startswith("get_ipython().run_cell_magic('codey'"):
                if "get_ipython().run_line_magic('load_ext', 'codey_assist'" in input_cell:
                    input_cell = input_cell.replace("get_ipython().run_line_magic('load_ext', 'codey_assist')", "")
                code_cells.append(input_cell)

        other_code = "\n".join(code_cells)
        generated_code = codegen.generate_code(line + "\n" + cell, other_code)
        print("Response is in the next cell!")

        self.shell.set_next_input(generated_code, replace=False)

    @line_magic
    def index(self, __):
        """Handler for the %index magic command."""
        # Find files in the current working directory and sub-directories
        all_files = []

        for root, _, files in os.walk(os.getcwd()):
            if (
                ".venv" in root
                or "__pycache__" in root
                or ".vscode" in root
                or ".idea" in root
                or ".git" in root
            ):
                continue

            for name in files:
                relative_path = os.path.relpath(os.path.join(root, name))
                all_files.append(relative_path)

        # Load documents, generate vectors and store in Vector database
        code_chunks = []
        for file in all_files:
            code_chunks.extend(code_qna_gen.chunk_code(file))

        code_qna_gen.create_index(code_chunks, persist_path=self.PERSIST_DIR)

    @cell_magic
    def code_qna(self, line, cell):
        """Handler for the %%code_qna magic command."""

        embeddings = VertexAIEmbeddings(
            model_name="textembedding-gecko@003",
        )

        db = Chroma(persist_directory=self.PERSIST_DIR, embedding_function=embeddings)

        code_qna_gen.answer_question(line + "\n" + cell, db)
