import logging
from tempfile import NamedTemporaryFile

import streamlit as st
from dotenv import load_dotenv
from engine import (
    YEN_PER_DOLLAR,
    calculate_price_as_doller,
    count_tokens,
    doller_to_yen,
    load_pdf,
    translate,
)
from langchain.callbacks.base import BaseCallbackHandler

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


st.set_page_config(layout="wide")

st.title("PDF Translator")

if "translated_list" not in st.session_state:
    st.session_state.translated_list = []

with st.sidebar:
    uploaded_file = st.file_uploader("Upload a file", type=["pdf"])

    clicked = st.button("Translate")

if uploaded_file is not None:
    file_name = uploaded_file.name

    with NamedTemporaryFile() as f:
        f.write(uploaded_file.getbuffer())
        tmp_file_name = f.name

        st.subheader(file_name)

        page_contents = load_pdf(tmp_file_name)

        translated_list = st.session_state.translated_list
        next_translate_index = len(translated_list)

        for i, page in enumerate(page_contents):
            st.caption(f"{i + 1}/{len(page_contents)}")

            left, right = st.columns(2)

            with left:
                text = page_contents[i]
                st.markdown(text)

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
            total_input_token_count = 0
            total_output_token_count = 0

            for page, translated in zip(page_contents, translated_list):
                total_input_token_count += count_tokens(page)
                total_output_token_count += count_tokens(translated)

            doller = calculate_price_as_doller(
                total_input_token_count, total_output_token_count
            )

            yen = doller_to_yen(doller)

            st.write(f"{total_input_token_count + total_output_token_count} tokens")
            st.write(f"${doller:.3f}")
            st.write(f"{yen:.1f} 円 (1ドル={YEN_PER_DOLLAR}円)")
