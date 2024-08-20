from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the Google Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], prompt])
    
    # Extract primary and secondary skills from the AI response
    primary_skills, secondary_skills = extract_skills_from_response(response.text)
    return primary_skills, secondary_skills

def extract_skills_from_response(response_text):
    primary_skills = []
    secondary_skills = []

    # Example extraction logic based on response text formatting
    primary_flag = False
    secondary_flag = False
    
    for line in response_text.splitlines():
        if "Primary Skills" in line:
            primary_flag = True
            secondary_flag = False
            continue
        elif "Secondary Skills" in line:
            primary_flag = False
            secondary_flag = True
            continue
        
        if primary_flag and line.strip():
            primary_skills.append(line.strip())
        elif secondary_flag and line.strip():
            secondary_skills.append(line.strip())
    
    return primary_skills, secondary_skills

def calculate_percentage(primary_skills, secondary_skills):
    # Assume each missing primary skill reduces percentage by 10%
    # and each missing secondary skill reduces it by 5%
    base_percentage = 100
    primary_skill_weight = 10
    secondary_skill_weight = 5
    
    percentage = base_percentage - (len(primary_skills) * primary_skill_weight) - (len(secondary_skills) * secondary_skill_weight)
    
    return max(0, percentage)  # Ensure percentage doesn't go below 0

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Specify the path to the Poppler binaries
        poppler_path = r'C:\Program Files (x86)\poppler\Library\bin'
        
        # Convert the PDF to images
        images = pdf2image.convert_from_bytes(
            uploaded_file.read(),
            poppler_path=poppler_path
        )

        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

## Streamlit App

st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage match")

input_prompt1 = """
You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. 
Please categorize the missing skills into "Primary Skills" (such as HTML, CSS, JS, MERN, etc.) and "Secondary Skills" (such as DevOps, GitHub, etc.). 
Based on these categories, list the missing skills separately and do not calculate the percentage match.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        primary_skills, secondary_skills = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("Missing Skills")
        st.write("Primary Skills: ", primary_skills)
        st.write("Secondary Skills: ", secondary_skills)
    else:
        st.write("Please upload the resume")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        primary_skills, secondary_skills = get_gemini_response(input_prompt3, pdf_content, input_text)
        percentage = calculate_percentage(primary_skills, secondary_skills)
        st.subheader("Percentage Match")
        st.write(f"Match Percentage: {percentage}%")
        st.write("Primary Skills: ", primary_skills)
        st.write("Secondary Skills: ", secondary_skills)
    else:
        st.write("Please upload the resume")