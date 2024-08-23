from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai
import fitz  # PyMuPDF
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(prompt, extracted_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    # Combine prompt and extracted text as input for the model
    combined_input = f"{prompt}\n\n{extracted_text}"
    response = model.generate_content([combined_input])
    return response.text

def get_gemini_response2(prompt2, input_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    # Combine prompt and extracted text as input for the model
    combined_input = f"{prompt2}\n\n{input_text}"
    response = model.generate_content([combined_input])
    return response.text



## Streamlit App

st.set_page_config(page_title="ATS Resume EXpert")
st.header("ATS Tracking System")
input_text=st.text_area("Job Description: ",key="input")
uploaded_file=st.file_uploader("Upload your resume(PDF)...",type=["pdf"])



if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

def extract_text_from_pdf(pdf_file):
    # Open the PDF
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    
    text = ""
    
    # Iterate through pages and extract text
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()

    return text

def calculate_skill_match(job_skills, resume_skills):
    job_skills_set = set(skill.strip().lower() for skill in job_skills)
    resume_skills_set = set(skill.strip().lower() for skill in resume_skills)
    
    matching_skills = job_skills_set.intersection(resume_skills_set)
    total_skills = len(job_skills_set)
   
    if total_skills == 0:
        return 0, matching_skills
    
    match_percentage = (len(matching_skills) / total_skills) * 100
    return match_percentage, matching_skills



if uploaded_file is not None:
    
    
    # Extract text from the uploaded PDF
    extracted_text = extract_text_from_pdf(uploaded_file)
    
    # Display extracted text
    st.subheader("Extracted Text")
    st.text_area("Resume Content:", value=extracted_text, height=300)



#submit2 = st.button("How Can I Improvise my Skills")

submit3 = st.button("Percentage match")



input_prompt1 = """
Get the skills mentioned in this job description. Don't add extra contents
"""
input_prompt3 = """
Get the skills mentioned in my resume. Put all the frameworks and technical skills in a single list. Don't add extra contents
"""



if submit3:
    if uploaded_file is not None:
        # Get the skills listed in the resume
        resume_skills_text = get_gemini_response(input_prompt3, extracted_text)
        job_skills_text = get_gemini_response2(input_prompt1, input_text)

        resume_skills = [skill.strip() for skill in resume_skills_text.split('\n') if skill.strip()]
        
        # Extract skills from the job description
        job_skills = [skill.strip() for skill in job_skills_text.split('\n') if skill.strip()]
        
        # Calculate match percentage
        match_percentage, matching_skills = calculate_skill_match(job_skills, resume_skills)
        
        st.subheader("Yout Skills:")
        st.write(resume_skills)
        st.subheader("Job requirement Skills:")

        st.write(job_skills)

        st.subheader("Match Percentage:")
        st.write(f"{int(match_percentage)}%")
        st.write(matching_skills)

    else:
        st.write("Please upload the resume")





