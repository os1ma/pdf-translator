import logging

import streamlit as st
import tiktoken
from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from pypdf import PdfReader

MODEL_NAME = "gpt-3.5-turbo"
INPUT_PRICE_PER_1K_TOKENS = 0.0015
OUTPUT_PRICE_PER_1K_TOKENS = 0.002
YEN_PER_DOLLAR = 140


load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StreamingStreamlitCallbackHandler(BaseCallbackHandler):
    def __init__(self, text_area):
        self.text_area = text_area
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.text_area.markdown(self.text)


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


st.set_page_config(layout="wide")

st.title("pdf-translator")

if "translated_list" not in st.session_state:
    st.session_state.translated_list = []

with st.sidebar:
    uploaded_file = st.file_uploader("Upload a file", type=["pdf"])

    clicked = st.button("Translate")

if uploaded_file is not None:
    file_name = uploaded_file.name
    st.subheader(file_name)

    pdf_reader = PdfReader(uploaded_file)
    pages = pdf_reader.pages

    translated_list = st.session_state.translated_list
    next_translate_index = len(translated_list)

    for i, page in enumerate(pages):
        st.caption(f"{i + 1}/{len(pages)}")

        left, right = st.columns(2)

        with left:
            text = pages[i].extract_text()
            st.text(text)

        with right:
            if i < len(translated_list):
                st.markdown(translated_list[i])
            elif i == next_translate_index:
                if clicked:
                    callback = StreamingStreamlitCallbackHandler(st.empty())
                    translated_text = translate(text, callback)
                    translated_list.append(translated_text)
            else:
                break

        st.divider()

    with st.sidebar:
        total_token_count = 0
        total_price = 0

        for page, translated in zip(pages, translated_list):
            input_token_count = count_tokens(page.extract_text())
            output_token_count = count_tokens(translated)
            total_token_count += input_token_count + output_token_count

            price = (
                input_token_count * INPUT_PRICE_PER_1K_TOKENS / 1000
                + output_token_count * OUTPUT_PRICE_PER_1K_TOKENS / 1000
            )
            total_price += price

        total_price_yen = total_price * YEN_PER_DOLLAR
        st.write(
            f"{total_token_count} tokens, ${total_price:.3f}, {total_price_yen:.1f} yen"
        )
