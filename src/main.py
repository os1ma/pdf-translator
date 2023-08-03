import logging

import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from pypdf import PdfReader

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
            "Please output in markdown format."
        ),
        HumanMessage(content=text),
    ]

    return chat(messages).content


st.set_page_config(layout="wide")

st.title("pdf-translator")

with st.sidebar:
    uploaded_file = st.file_uploader("Upload a file", type=["pdf"])

    clicked = st.button("Translate")

if "translated_list" not in st.session_state:
    st.session_state.translated_list = []

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
            text = pages[0].extract_text()
            st.text(text)

        with right:
            if i < len(translated_list):
                st.text(translated_list[i])
            elif i == next_translate_index:
                if clicked:
                    text_area = st.empty()

                    translated_text = translate(text)

                    text_area.markdown(translated_text)
                    translated_list.append(translated_text)
            else:
                break

        st.divider()
