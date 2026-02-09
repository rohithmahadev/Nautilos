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
from utils import parsing_pdf
load_dotenv()

from utils import parsing_pdf, accomplishments_pdf 

if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None

if 'json_parsed_job_data' not in st.session_state:
    st.session_state.json_parsed_job_data = None

if 'json_parsed_pdf_data' not in st.session_state:
    st.session_state.json_parsed_pdf_data = None

if 'json_parsed_final_output' not in st.session_state:
    st.session_state.json_parsed_final_output = None

# Set env var from Streamlit secrets
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
)

st.title("Career Coach Nautilos V1.0")



uploaded_pdf_file = st.file_uploader("Upload a PDF version of your resume",
                                     type= "pdf",
                                     accept_multiple_files= False)
        
st.session_state.pdf_data = parsing_pdf(uploaded_pdf_file)



st.header("Enter the job description link")

st.markdown("Note: Must be open source")

website = st.text_input("Link: ")



### LLM 

prompt_extract = PromptTemplate.from_template(
 """
 ##Job Description
 {page_data}
 ### Instruction:
 The scrapted text is from the career's page of a company's website. Look in detail for the skills. It might be in other headings too. The instruction for you is to extract the job posting, skills, experience and salary and return them in JSON format containing the 
 follwing keys:

Role:
Experience:
Skills (Give 5-10 skills in a list format):
Description:
Salary: (only if mentioned):

Only return the valid JSON file.

### Valid JSON Format without any preamble
 
 """ 
)


json_parser = JsonOutputParser()
# Inside the button click
if st.button("Submit"):

    
    # Validation checks
    if website == "" or website is None:
        st.error("⚠️ Please enter a job description link to proceed!")
    elif uploaded_pdf_file is None:
        st.error("⚠️ Please upload your resume PDF to proceed!")
    else:
        with st.spinner("Loading job data..."):
            loader = WebBaseLoader(website)
            st.session_state.page_data = loader.load()
            chain_extract = prompt_extract | llm
            res = chain_extract.invoke(input={'page_data': st.session_state.page_data})
            st.session_state.json_parsed_job_data = json_parser.parse(res.content)
            # st.write("Data collected from the link",st.session_state.json_parsed_job_data)

            display_data = st.session_state.json_parsed_job_data.copy()
            df = pd.DataFrame([display_data]).T  # .T transposes it
            df.columns = ['Job Description Details']
            st.table(df)
           
            
        st.success("✅ Job data loaded successfully!") 

    prompt_extract_resume_pdf = PromptTemplate.from_template(
    """
    ##Job Description
    {pdf_data}
    ### Instruction:
    The scrapted text is from the resume of the user. The instruction for you is to extract the skills, certifications and relavent experience and return them in JSON format containing the 
    follwing keys:

    Skills:
    Experience (5-6 lines based on the resume):
    
    Note: Extract relavent experience as a summary and not individually. No need to mention company name and duration. extract the relavent exp from the work exp details section if available.
    
    Certification:

    Only return the valid JSON file.

    ### Valid JSON Format without any preamble
    
    """ 
    )


    chain_extract_pdf_data = prompt_extract_resume_pdf | llm
    res_pdf = chain_extract_pdf_data.invoke(input = {'pdf_data': st.session_state.pdf_data})

    json_parser = JsonOutputParser()
    st.session_state.json_parsed_pdf_data = json_parser.parse(res_pdf.content)
    # st.write("Data collected from the resume",json_parsed_pdf_data)
    display_data = st.session_state.json_parsed_pdf_data.copy()
    df = pd.DataFrame([display_data]).T  # .T transposes it
    df.columns = ['Skills extracted from the Resume']
    st.table(df)



    prompt_comparsion = PromptTemplate.from_template(
    """
    ##Job Description
    {json_parsed_job_data}, 
    
    ###User resume data 
    {json_parsed_pdf_data}
    ### Instruction:

    
    You are a smart job matcher. You already have two jsons. The jsons are returned from job description and the pdf (resume) which the user uploads.
    Instructions for you
    1. Compare the job skills listed in the job desciption vs the job skills on the resume and return the matching skills. You can match to a near extend of 50% relavancy but not beyond. IF the skills is unrelated, make it unmatched skill. Use semantic searching matching
    Example 1: If a person has data science experinence but never worked with big data technologies like sqoop, kafka, then its unmatched skill.
    Example 2: If a person has SQL experience but no kafka, Flume, Pig, then SQL goes into matched and the others go into unmatched.
    Example 3: If a person has data science python experience, do not assume the person knows everything on python. Look for specific frameworks and other programming languages
    
    2. Return the list of skills that the user lacks based on the job data
    3. Give a score out of 10 based on the job suitability. Remember to be a fair grader. Look for the seniority mentioned. The grade should be based on 80% matched skills and 20% unmatched skills. 
    4. Give a one-two liner whether you advise the person to apply for the job or not purely based on the skills provided
    5. Give a recommendation on the core technologies to concentrate or learn based on the input. 
    ### Return a response in the following JSON format without preamble:

    Matched Skills: 
    Unmatched Skills (only skills that are not in the resume based on the job description):
    Job Suitability Score
    Advice:
    Recommendation:


    """ 
        
    )


    chain_extract_jop_matching = prompt_comparsion | llm
    res_matching = chain_extract_jop_matching.invoke(input = {'json_parsed_job_data': st.session_state.json_parsed_job_data, "json_parsed_pdf_data":st.session_state.json_parsed_pdf_data})
    print(res_matching.content)


    st.session_state.json_parsed_final_output = json_parser.parse(res_matching.content)
    # st.write(st.session_state.json_parsed_final_output)
    display_data = st.session_state.json_parsed_final_output.copy()
    df = pd.DataFrame([display_data]).T  # .T transposes it
    results = st.session_state.json_parsed_final_output

    st.subheader("🎯 Job Match Analysis")

    # Score as a metric
    col1, col2, col3 = st.columns(3)
    with col2:
        st.metric("Match Score", f"{results['Job Suitability Score']}/10")

    # Matched skills
    st.success("✅ **Matched Skills**")
    st.write(", ".join(results['Matched Skills']) if isinstance(results['Matched Skills'], list) else results['Matched Skills'])

    # Unmatched skills
    st.warning("⚠️ **Skills to Develop**")
    st.write(", ".join(results['Unmatched Skills']) if isinstance(results['Unmatched Skills'], list) else results['Unmatched Skills'])

    # Advice
    st.info(f"**💡 Recommendation:** {results['Advice'],results['Recommendation']}")


