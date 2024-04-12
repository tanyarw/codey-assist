"""Module to answer code queries"""

import vertexai
from typing import List
import vertexai
from vertexai.language_models import TextGenerationModel
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.schema import Document
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)

vertexai.init(project="gdc-ai-playground", location="us-central1")


def chunk_code(file_name):
    """Chunks a code file into smaller units."""
    chunked_code = []

    if file_name.endswith(".py"):
        python_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=1000, chunk_overlap=200
        )
        with open(file_name, "r") as f:
            code = f.read()
            chunked_code = python_splitter.create_documents(
                [code], metadatas=[{"source": file_name}]
            )

    elif file_name.endswith(".js"):
        js_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.JS, chunk_size=1000, chunk_overlap=200
        )
        with open(file_name, "r") as f:
            code = f.read()
            chunked_code = js_splitter.create_documents(
                [code], metadatas=[{"source": file_name}]
            )

    elif file_name.endswith(".md"):
        js_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.MARKDOWN, chunk_size=1000, chunk_overlap=200
        )
        with open(file_name, "r") as f:
            code = f.read()
            chunked_code = js_splitter.create_documents(
                [code], metadatas=[{"source": file_name}]
            )

    return chunked_code


def create_index(
    code_chunks: List[Document],
    persist_path: str,
):
    """Embeds texts with a pre-trained, foundational model and creates Chroma DB index."""

    embeddings = VertexAIEmbeddings(
        model_name="textembedding-gecko@003",
    )

    print("Building index...")

    db = Chroma.from_documents(
        documents=code_chunks, embedding=embeddings, persist_directory=persist_path
    )
    db.persist()  # Ensure DB persist

    print("Index built.")


def answer_question(question, db):
    """Generates code response based on the question"""

    template = """You are helpful coding assistant that has experience in coding. You're tasked to answer the user's question based on the code provided. If you cannot answer the question, ask user to rephrase and provide more context to assist code search.

Code:
{context}

Examples:
Q: <A question about how to use a function>
A: <explain args and return value, show a simple accurate code example>
Files: <relevant source files>

Q: <A question about an error the user is facing>
A: <Diagnose how the error is related to the code, and suggest code fix>
Files: <relevant source files>

Q: <A question asking which function to call for a feature>
A: <A description of the function and code snippet of how it can be used for the feature>
Files: <relevant source files>

Q: <A question about how to add a feature to the code base>
A: <Clear explanation and suggestions with code snippets to implement the feature>
Files: <relevant source files>

User's question: {input}

Helpful answer:
    """

    # Create the retrieval chain
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    docs = retriever.get_relevant_documents(question)

    context = ""
    for _doc in docs:
        context += "Source File: " + _doc.metadata["source"] + "\n"
        context += "Source Code:\n" + _doc.page_content + "_ " * 20 + "\n"

    model = TextGenerationModel.from_pretrained("text-bison-32k")
    response = model.predict(
        template.format(context=context, input=question),
        temperature=0.4,
        max_output_tokens=4096,
    )

    print(response.text)
