import streamlit as st 
import pandas as pd 
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os
from dotenv import load_dotenv 
import pandas as pd

import os

from groq import Groq
from langchain_groq import ChatGroq

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()



def parsing_pdf(uploaded_pdf_file):
    if uploaded_pdf_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_pdf_file.read())
                tmp_path = tmp_file.name

            loader = PyPDFLoader(
                tmp_path,
                mode="single",
                pages_delimiter="\n-------THIS IS A CUSTOM END OF PAGE-------\n",
            )
            
            
            parsed_pdf_data  = loader.load()
            st.text('Loading data...done!')

            return parsed_pdf_data
    
def accomplishments_pdf(uploaded_accomplishments_pdf_file):
    if uploaded_accomplishments_pdf_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_accomplishments_pdf_file.read())
            tmp_path = tmp_file.name

        loader = PyPDFLoader(
            tmp_path,
            mode="single",
            pages_delimiter="\n-------THIS IS A CUSTOM END OF PAGE-------\n",
        )
        
        
        accomplishment_data  = loader.load()
        st.text('Loading data...accomplishments done!')

        return accomplishment_data
