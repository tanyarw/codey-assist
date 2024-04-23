"""Module to answer code queries"""

import ast
import os
from typing import List
import subprocess

import vertexai
from vertexai.generative_models import GenerativeModel
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)

vertexai.init(location="us-central1")

def chunk_code(file_name: str) -> List[Document]:
    """Chunks a code file into smaller units."""
    chunked_code = []

    # Python splitter
    if file_name.endswith(".py"):
        with open(file_name, "r") as f:
            code = f.read()
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    chunked_code.append(
                        Document(
                            page_content=ast.unparse(node),
                            metadata={"source": file_name},
                        )
                    )

    # JS splitter
    elif file_name.endswith(".js"):
        js_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.JS)
        with open(file_name, "r") as f:
            code = f.read()
            chunked_code = js_splitter.create_documents(
                [code], metadatas=[{"source": file_name}]
            )

    # GO splitter
    elif file_name.endswith(".go"):
        go_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.GO)
        with open(file_name, "r") as f:
            code = f.read()
            chunked_code = go_splitter.create_documents(
                [code], metadatas=[{"source": file_name}]
            )

    # TS splitter
    elif file_name.endswith(".ts"):
        ts_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.TS)
        with open(file_name, "r") as f:
            code = f.read()
            chunked_code = ts_splitter.create_documents(
                [code], metadatas=[{"source": file_name}]
            )

    # TS splitter
    elif file_name.endswith(".java"):
        java_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.JAVA
        )
        with open(file_name, "r") as f:
            code = f.read()
            chunked_code = java_splitter.create_documents(
                [code], metadatas=[{"source": file_name}]
            )

    # HTML splitter
    elif file_name.endswith(".html"):
        html_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.HTML
        )
        with open(file_name, "r") as f:
            code = f.read()
            chunked_code = html_splitter.create_documents(
                [code], metadatas=[{"source": file_name}]
            )

    # Markdown splitter
    elif file_name.endswith(".md"):
        md_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.MARKDOWN
        )
        with open(file_name, "r") as f:
            code = f.read()
            chunked_code = md_splitter.create_documents(
                [code], metadatas=[{"source": file_name}]
            )

    return chunked_code

def create_index(
    code_chunks: List[Document],
    persist_path: str,
) -> None:
    """Embeds texts with a pre-trained, foundational model and creates Chroma DB index."""

    print(f"Building index around {persist_path}")

    # Create index from chunked code
    db = Chroma.from_documents(
        documents=code_chunks,
        embedding=VertexAIEmbeddings(
            model_name="textembedding-gecko@003",
        ),
        persist_directory=persist_path,
    )

    # Ensure DB persist
    db.persist()
    print(f"Index built at {persist_path}.")


def answer_question(question, db) -> str:
    """Generates code response based on the question"""

    template = """You are helpful coding assistant that has experience in coding. You're tasked to answer the user's question based on the code provided. Give a peek into the relevant code snippet, since the user can't see it. If you cannot answer the question, ask user to rephrase and provide more context to assist code search.

Code:
{context}

Question: {input}
Please list the relevant source code file names as well.
Answer:"""

    # Create the retrieval chain
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    docs = retriever.get_relevant_documents(question)

    context = ""
    for _doc in docs:
        context += "Source File: " + _doc.metadata["source"] + "\n"
        context += "Source Code:\n" + _doc.page_content + "\n" + "_ " * 20 + "\n"

    print(context)
    model = GenerativeModel("gemini-1.0-pro-002")
    response = model.generate_content(
        template.format(context=context, input=question),
        generation_config={
            "max_output_tokens": 4096,
            "temperature": 1,
            "top_p": 1,
        },
    )

    return response.text


def get_changed_files_in_dir(directory_path):
    """Fetches the names of changed files within a directory in a Git repository."""

    select_files = []

    cwd = os.getcwd()

    os.chdir(directory_path)
    result = subprocess.run(
        ["git", "diff", "--name-only", directory_path],
        check=True,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    changed_files = result.stdout.splitlines()

    os.chdir(cwd)
    select_files = [
        os.path.join(directory_path, f.split("/")[-1])
        for f in changed_files
        if f.endswith((".py", ".js", ".md", ".html", ".ts", ".go", ".java"))
    ]

    return select_files


def get_documents_by_source(db, source_filename):
    """Retrieves documents from a ChromaDB where metadata['source'] matches the filename."""

    doc_ids = db.get()["ids"]
    metadatas = db.get()["metadatas"]
    changed_ids = []

    for index, data in enumerate(metadatas):
        if data["source"] == source_filename:
            changed_ids.append(doc_ids[index])

    return changed_ids
