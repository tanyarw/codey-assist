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
    """Chunks a code file into smaller units under 512 characters."""
    chunked_code = []

    if file_name.endswith(".py"):
        python_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=1000, chunk_overlap=100
        )
        with open(file_name, "r") as f:
            code = f.read()
            chunked_code = python_splitter.create_documents(
                [code], metadatas=[{"source": file_name}]
            )

    elif file_name.endswith(".js"):
        js_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.JS, chunk_size=1000, chunk_overlap=100
        )
        with open(file_name, "r") as f:
            code = f.read()
            chunked_code = js_splitter.create_documents(
                [code], metadatas=[{"source": file_name}]
            )

    return chunked_code


def create_index(
    code_chunks: List[Document],
    persist_path: str = "./.tmp/index",
):
    """Embeds texts with a pre-trained, foundational model and creates Chroma DB index."""

    embeddings = VertexAIEmbeddings(
        model_name="textembedding-gecko@003",
    )

    db = Chroma.from_documents(
        documents=code_chunks, embedding=embeddings, persist_directory=persist_path
    )
    db.persist()  # Ensure DB persist

    return db


def answer_question(question, db):
    """Generates code response based on the question"""

    template = """
You are helpful coding assistant that has experience in coding. You're tasked to answer the user's question, based on the code context provided.
code context:
{context}


user's question:
{input}

If you cannot find an answer ask the user to rephrase the question.
answer:
    """

    # Create the retrieval chain
    model = TextGenerationModel.from_pretrained("code-bison-32k")

    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    docs = retriever.get_relevant_documents(question)

    context = ""
    for d in docs:
        context += d.page_content + "\n" + "_ " * 20 + "\n"

    response = model.predict(
        template.format(context=context, input=question),
        temperature=0.2,
        max_output_tokens=2048,
    )

    print(response.text)
