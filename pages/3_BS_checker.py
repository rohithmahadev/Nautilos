
import streamlit as st 
import os
from dotenv import load_dotenv 

from langchain_groq import ChatGroq

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate

load_dotenv()




# Set env var from Streamlit secrets
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
)



st.header("# Enter the job description link that you want to check for")

st.markdown("Note: Must be open source")

website = st.text_input("Link: ")


st.write("## Check if the JD is BS or not!")

if st.button("Check for BS!"):
            # Convert list of Documents to plain text
    # Validation checks
    if website == "" or website is None:
        st.error("⚠️ Please enter a job description link to proceed!")
    else:
        with st.spinner("Checking for BS in the career page.."):
            loader = WebBaseLoader(website)
            st.session_state.page_data = loader.load()
            extracted_text = " ".join([doc.page_content for doc in st.session_state.page_data])
            prompt_jd_eval = PromptTemplate.from_template(
                        """
                                           
                        You are an expert career analyst evaluating job descriptions for realism and fairness.

                        ## Job Description
                        {Extracted_job_text}

                        ## Your Task
                        Analyze this job posting objectively and fairly. Most job descriptions are reasonable with some stretch goals - only flag as "BS" if there are SIGNIFICANT red flags.

                        ## Evaluation Criteria

                        **Check for balance between:**
                        1. Required skills vs. stated responsibilities (do they align?)
                        2. Experience level vs. scope of work (is 2 years experience expected to do 10 years of work?)
                        3. Compensation/seniority vs. expectations (junior pay for senior responsibilities?)
                        4. Specificity vs. vagueness (are requirements measurable or just buzzwords?)

                        **Red flags that indicate "BS":**
                        - Requiring 5+ years experience for entry-level pay
                        - Expecting expertise in 10+ unrelated technologies
                        - Responsibilities that would require multiple full-time roles
                        - Contradictory requirements (e.g., "entry level" but "8+ years experience")
                        - Extremely vague job duties with unrealistic skill requirements
                        - Very high breadth of skills required for one particular role
                        - Skils that are on different ends for example data scientist with C++ experience, MLOps engineer with math foundation

                        **What's NOT BS:**
                        - Some stretch goals or aspirational skills
                        - A mix of required and "nice to have" skills
                        - Broad responsibilities (common in smaller companies)
                        - Industry-standard requirements for the role level

                        ## Output Format

                        ### **Summary:** 
                        [1-2 sentences describing the role]

                        ### **Salary**
                        [Mention only the salary range or the number]

                        ### **Analysis:**
                        [Balanced assessment of strengths and concerns]

                        ### **Concerns (if any):**
                        - [Specific red flag 1, if exists]
                        - [Specific red flag 2, if exists]

                        ## **Verdict:** <BS or NOT BS>

                        # **Reasoning:** [1-2 sentences explaining your verdict based on the severity of concerns vs. overall reasonableness]


                        ## Note: if the job description is not provided due to a Cloudflare block return "None" 

                        """
                    )

                    # Create chain
            chain_extract_job_eval = prompt_jd_eval | llm

                
            res_matching_job_eval = chain_extract_job_eval.invoke(
                        input = {"Extracted_job_text":extracted_text}
                    )

            st.write(res_matching_job_eval.content)
