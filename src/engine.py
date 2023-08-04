import sys

import tiktoken
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.schema import HumanMessage, SystemMessage

MODEL_NAME = "gpt-3.5-turbo"


def translate(text: str, callback) -> str:
    chat = ChatOpenAI(
        model_name=MODEL_NAME,
        temperature=0,
        streaming=True,
        callbacks=[callback],
    )

    messages = [
        SystemMessage(
            content="Please translate the following English text into Japanese."
            "Please output in markdown format."
            "Input text is extracted from PDF so it may contain unnecessary parts."
        ),
        HumanMessage(content=text),
    ]

    return chat(messages).content


def count_tokens(text):
    encoding = tiktoken.encoding_for_model(MODEL_NAME)
    tokens = encoding.encode(text)
    return len(tokens)


def load(file_path: str) -> list[str]:
    loader = UnstructuredPDFLoader(file_path=file_path, mode="elements")
    docs = loader.load()

    last_doc = docs[-1]
    last_doc_page_number = last_doc.metadata["page_number"]

    texts = [""] * last_doc_page_number

    for doc in docs:
        metadata = doc.metadata
        page_number = metadata["page_number"]
        category = metadata["category"]

        if category == "Title":
            texts[page_number - 1] += f"# {doc.page_content}\n\n"
            pass
        elif category == "NarrativeText":
            texts[page_number - 1] += doc.page_content + "\n\n"
        elif category in ["UncategorizedText", "ListItem"]:
            pass
        else:
            raise ValueError(f"Unknown category: {category}")

    return texts


if __name__ == "__main__":
    file_path = sys.argv[1]
    texts = load(file_path)
    for i, text in enumerate(texts):
        print(f"========== Page {i+1} ==========")
        print(text)