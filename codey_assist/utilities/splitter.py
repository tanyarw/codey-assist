"""Module for chunking code files into smaller units."""

import ast
from typing import List

from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from langchain_core.documents import Document


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
