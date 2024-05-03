"""Extension for the magic commands."""

import os
from IPython.core.magic import line_magic, cell_magic, Magics, magics_class
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.vectorstores.chroma import Chroma

from codey_assist import codegen, code_qna_gen
from codey_assist.utilities import splitter, changed_files

@magics_class
class CodeyMagic(Magics):
    """Class for the magic commands."""

    def __init__(self, shell):
        super().__init__(shell)  # Initialize the parent class
        self.shell = shell  # Store the IPython instance
        self.persist_path = ".tmp/"

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

    def index(self, line):
        """Creates a new index DB."""
        self.persist_path = os.path.join(os.path.abspath(line), self.persist_path)
        line = os.path.abspath(line)

        ignore_patterns_dict = changed_files.get_ignore_patterns_dict(line)
        # Find files in the current working directory and sub-directories
        all_files = []

        for root, _, files in os.walk(line):

            # Find all other files
            for name in files:
                fp = os.path.join(root, name)

                if not changed_files.should_ignore(fp, ignore_patterns_dict):
                    print(f"Adding: {fp}")
                    all_files.append(os.path.abspath(fp))

        # Split code into chunks
        code_chunks = []
        for file in all_files:
            code_chunks.extend(splitter.chunk_code(file))

        # Create Chroma DB index with chunked code
        code_qna_gen.create_index(code_chunks, persist_path=self.persist_path)

    @line_magic
    def set_index(self, line):
        """Sets the path for the index."""
        line = os.path.abspath(line)
        if not line.endswith(".tmp/") or not line.endswith(".tmp"):
            line = os.path.join(line, ".tmp/")

        if not os.path.exists(line) or not os.listdir(line):
            # create index
            self.index(line.replace(".tmp/", "").replace(".tmp", ""))
        else:
            self.persist_path = line

            # Load index
            print("Loading index...")
            db = Chroma(
                persist_directory=self.persist_path,
                embedding_function=VertexAIEmbeddings(
                    model_name="textembedding-gecko@003",
                ),
            )

            # find changed files in parent directory
            print("Finding staged files...")
            modified_files = changed_files.get_changed_files_in_dir(
                os.path.dirname(self.persist_path)
                .replace(".tmp/", "")
                .replace(".tmp", "")
            )

            if modified_files:
                not_updated = False
                for status, files in modified_files.items():
                    if status == "D":
                        for f in files:
                            doc_ids = code_qna_gen.get_documents_by_source(db, f)

                            if doc_ids:
                                print(f"Deleting doc {f}")
                                db.delete(doc_ids)
                            else:
                                print(f"Couldn't delete {f}")

                    elif status == "M":
                        for f in files:
                            doc_ids = code_qna_gen.get_documents_by_source(db, f)

                            if doc_ids:
                                code_to_add = splitter.chunk_code(f)

                                if code_to_add:
                                    print(f"Updating doc {f}")
                                    db.delete(doc_ids)
                                    db.add_documents(code_to_add)
                                else:
                                    print(f"Not enough code context to update {f}")

                            else:
                                print(f"Couldn't update {f}")

                    elif status == "A":
                        for f in files:
                            code_to_add = splitter.chunk_code(f)
                            if code_to_add:
                                print(f"Adding doc {f}")
                                db.add_documents(code_to_add)
                            else:
                                print(f"Not enough code context to add {f}")
                    else:
                        not_updated = True

                if not_updated:
                    print("No updates to index.")
                else:
                    print("Done.")

    @cell_magic
    def code_qna(self, line, cell):
        """Handler for the %%code_qna magic command."""

        # Load index
        db = Chroma(
            persist_directory=self.persist_path,
            embedding_function=VertexAIEmbeddings(
                model_name="textembedding-gecko@003",
            ),
        )

        # Retrieve relevant code chunks and generate a response
        answer = code_qna_gen.answer_question(line + "\n" + cell, db)

        print(answer)
