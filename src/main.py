import logging

import click
from dotenv import load_dotenv
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.schema import HumanMessage, SystemMessage

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def translate(text: str) -> str:
    chat = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )

    messages = [
        SystemMessage(
            content="Please translate the following English text into Japanese."
        ),
        HumanMessage(content=text),
    ]

    return chat(messages).content


@click.command()
@click.option("--file", "-f", help="Path to the PDF file")
def main(file: str) -> None:
    logger.info(f"Loading file {file}")

    loader = PyPDFLoader(file_path=file)
    pages = loader.load_and_split()
    total_page_number = len(pages)
    logger.info(f"Loaded {total_page_number} pages")

    for i, page in enumerate(pages):
        logger.info(f"Translate page {i + 1}/{total_page_number}")

        text = page.page_content
        translate(text)

        input("Press Enter to continue...")


if __name__ == "__main__":
    main()
