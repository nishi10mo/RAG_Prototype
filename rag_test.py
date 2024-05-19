# -*- coding: utf-8 -*-
"""RAG_test.ipynb

Automatically generated by Colab.

"""

!pip install -q langchain
!pip install -q openai
!pip install -q sentence_transformers
# !pip install -q spacy
!pip install -q chromadb
!pip install -q optimum
!pip install -q auto-gptq --extra-index-url https://huggingface.github.io/autogptq-index/whl/cu122/
!pip install -q gradio
!pip install -q accelerate
!python -m spacy download ja_core_news_sm

from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import SpacyTextSplitter
from langchain.vectorstores import Chroma

loader = CSVLoader(file_path='./csv_test.csv')
loader = CSVLoader(file_path='csv_test.csv',
                   source_column='詳細',
                   metadata_columns=['件名'],
                   encoding='CP932',
                   csv_args={"delimiter": ','})
documents = loader.load()

text_splitter = SpacyTextSplitter(
    chunk_size=300,
    pipeline="ja_core_news_sm"
)
splitted_documents = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name="oshizo/sbert-jsnli-luke-japanese-base-lite")

database = Chroma(
    persist_directory="./.data_csv",
    embedding_function=embeddings
)

database.add_documents(
    splitted_documents,
)

print("データベースの作成が完了しました。")

API_KEY = ""

import torch
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.chat_models import ChatOpenAI
import gradio as gr

with gr.Blocks() as demo:

    chatbot = gr.Chatbot()
    msg = gr.Textbox(show_label=False, placeholder="業務について分からないことがあれば聞いてください")
    clear = gr.ClearButton([msg, chatbot])

    llm = ChatOpenAI(openai_api_key=API_KEY, model_name="gpt-4-1106-preview", temperature=0)

    retriever = database.as_retriever()

    qa = RetrievalQA.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    def chat(prompt, message_history):
        global qa

        result = qa(prompt)["result"]

        message_history.append((prompt, result))

        return "", message_history

    msg.submit(chat, [msg, chatbot], [msg, chatbot])

demo.queue()
demo.launch()