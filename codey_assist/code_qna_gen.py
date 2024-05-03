"""Module to answer code queries"""

from typing import List

import vertexai
from vertexai.generative_models import GenerativeModel
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_core.documents import Document

vertexai.init(location="us-central1")

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


def get_documents_by_source(db, source_filename):
    """Retrieves documents from a ChromaDB where metadata['source'] matches the filename."""

    doc_ids = db.get()["ids"]
    metadatas = db.get()["metadatas"]
    changed_ids = []

    for index, data in enumerate(metadatas):
        if data["source"] == source_filename:
            changed_ids.append(doc_ids[index])

    return changed_ids


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
