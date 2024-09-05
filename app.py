from dotenv import load_dotenv
import os
import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import re

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Predefined domain skills
domain_skills = {
    'Computer Science': ["Python", "Java", "JavaScript", "SQL", "HTML", "CSS", "Django", "Flask", "React", "Node.js", "C", "C++", "Spring Boot", "Thymeleaf", "ProjectManagement","ReactJS"],
    'Electronics': ["Circuit Design", "Signal Processing", "Embedded Systems", "Analog Electronics", "Digital Electronics", "Communication Systems"],
    'Mechanical': ["Thermodynamics", "Fluid Mechanics", "Material Science", "Manufacturing Processes", "Dynamics", "Control Systems"],
    'Electrical': ["Power Systems", "Electrical Machines", "Control Systems", "Power Electronics", "Signal Processing", "Renewable Energy Systems"]
}

# Function to get response from Gemini API
def get_gemini_response(prompt, extracted_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    combined_input = f"{prompt}\n\n{extracted_text}"
    response = model.generate_content([combined_input])
    return response.text

# Extract text from the uploaded PDF
def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Normalize and map domain to predefined categories
def map_domain(extracted_domain):
    domain_mapping = {
        'computer science': 'Computer Science',
        'electronics': 'Electronics',
        'mechanical': 'Mechanical',
        'electrical': 'Electrical'
    }
    # Normalize extracted domain
    normalized_domain = extracted_domain.lower()
    for key in domain_mapping:
        if key in normalized_domain:
            return domain_mapping[key]
    return "Unknown"

# Calculate skill match and percentage
def calculate_skill_match(domain, resume_skills):
    skill_keywords = domain_skills.get(domain, [])
    print(skill_keywords)
    resume_skills = [skill.strip().lower() for skill in resume_skills]
    matching_skills = set(skill for skill in resume_skills if skill in [s.lower() for s in skill_keywords])
    print(resume_skills)
    total_skills = len(skill_keywords)
    
    if total_skills == 0:
        return 0, matching_skills
    
    match_percentage = (len(matching_skills) / total_skills) * 100
    return match_percentage, matching_skills

# Streamlit UI setup
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])
def clean_skill(skill):
    # Remove leading/trailing dashes and extra spaces
    return skill.replace('-', '').strip()

def extract_and_clean_skills(resume_skills_text):
    # Extract and clean skills
    return [clean_skill(skill) for skill in resume_skills_text.split('\n') if skill.strip()]

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

    # Extract text from the uploaded PDF
    extracted_text = extract_text_from_pdf(uploaded_file)
    
    # Display extracted text
    st.subheader("Extracted Text")
    st.text_area("Resume Content:", value=extracted_text, height=300)

    # Define prompts for Gemini API
    input_prompt_degree = """
    Get the degree with domain mentioned in this resume like (BE Computer Science and Engineering, BE Electronics, or BTech IT). Don't add extra contents, just give me the actual degree with domain.
    """
    
    input_prompt_skills = """
    Get the skills mentioned in my resume. Don't add extra contents. Just give me the technical skills
    """

    # Extract skills and domain using Gemini API
    resume_skills_text = get_gemini_response(input_prompt_skills, extracted_text)
    extracted_domain = get_gemini_response(input_prompt_degree, extracted_text).strip()

    # Map the extracted domain to a more general category
    domain = map_domain(extracted_domain)

    # Process the extracted skills
    # resume_skills = [skill.strip() for skill in resume_skills_text.split('\n') if skill.strip()]
    resume_skills = extract_and_clean_skills(resume_skills_text)

    st.subheader("Extracted Skills:")
    st.write(resume_skills)
    
    st.subheader("Extracted Domain:")
    st.write(extracted_domain)


    # Match the skills with the corresponding domain
    if domain and domain != "Unknown":
        match_percentage, matching_skills = calculate_skill_match(domain, resume_skills)
        
        st.subheader("Matched Skills:")
        st.write(matching_skills)
        st.subheader("Match Percentage:")
        st.write(f"{int(match_percentage)}%")
    else:
        st.write("Unable to determine the domain from the extracted degree or domain is unknown")
else:
    st.write("Please upload the resume")




















































# from dotenv import load_dotenv

# load_dotenv()
# import base64
# import streamlit as st
# import os
# import io
# from PIL import Image 
# import pdf2image
# import fitz  # PyMuPDF
# import re

# domain_skills = {
#     'Computer Science': ["Python", "Java", "JavaScript", "SQL", "HTML", "CSS", "Django", "Flask", "React", "Node.js", "C", "C++", "Spring Boot", "Thymeleaf","Project-Management"],
#     'Electronics': ["Circuit Design", "Signal Processing", "Embedded Systems", "Analog Electronics", "Digital Electronics", "Communication Systems"],
#     'Mechanical': ["Thermodynamics", "Fluid Mechanics", "Material Science", "Manufacturing Processes", "Dynamics", "Control Systems"],
#     'Electrical': ["Power Systems", "Electrical Machines", "Control Systems", "Power Electronics", "Signal Processing", "Renewable Energy Systems"]
# }

# def extract_degree(text):
 
#     degree_patterns = [
#         r'\bB\.?E\b[\-\s]?[A-Za-z\s]+',  # Matches "B.E" or "BE"
#         r'\bB\.?Tech\b[\-\s]?[A-Za-z\s]+',  # Matches "B.Tech"
#         r'\bM\.?E\b[\-\s]?[A-Za-z\s]+',  # Matches "M.E"
#         r'\bM\.?Tech\b[\-\s]?[A-Za-z\s]+',  # Matches "M.Tech"
#         r'\bPh\.?D\b[\-\s]?[A-Za-z\s]+',  # Matches "Ph.D"
#         r'\b(?:Bachelor(?: of)?(?: Science| Engineering| Arts| Commerce)?(?: in)?)\b[\-\s]?[A-Za-z\s]+',
#         r'\b(?:Master(?: of)?(?: Science| Engineering| Arts| Commerce)?(?: in)?)\b[\-\s]?[A-Za-z\s]+'
#     ]
    
#     for pattern in degree_patterns:
#         matches = re.findall(pattern, text, re.IGNORECASE)
#         if matches:

#             degree_text = max(matches, key=len).strip()
       
#             if 'computer' in degree_text.lower():
#                 return 'Computer Science', degree_text
#             elif 'electronics' in degree_text.lower():
#                 return 'Electronics', degree_text
#             elif 'mechanical' in degree_text.lower():
#                 return 'Mechanical', degree_text
#             elif 'electrical' in degree_text.lower():
#                 return 'Electrical', degree_text
#             return degree_text
#     return "Degree not found", None

# def extract_skills_from_text(text, skill_keywords):
#     skills = []
#     for keyword in skill_keywords:
#         if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
#             skills.append(keyword)
#     return skills

# st.set_page_config(page_title="ATS Resume Expert")
# st.header("ATS Tracking System")
# uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

# if uploaded_file is not None:
#     st.write("PDF Uploaded Successfully")

# def extract_text_from_pdf(pdf_file):
#     pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
#     text = ""
#     for page_num in range(len(pdf_document)):
#         page = pdf_document.load_page(page_num)
#         text += page.get_text()
#     return text

# def calculate_skill_match(domain, resume_skills):
#     skill_keywords = domain_skills.get(domain, [])
#     resume_skills = extract_skills_from_text(resume_skills, skill_keywords)
#     matching_skills = set(skill.strip().lower() for skill in resume_skills)
#     total_skills = len(skill_keywords)
#     if total_skills == 0:
#         return 0, matching_skills
#     match_percentage = (len(matching_skills) / total_skills) * 100
#     return match_percentage, matching_skills

# if uploaded_file is not None:
#     extracted_text = extract_text_from_pdf(uploaded_file)

#     st.subheader("Extracted Text")
#     st.text_area("Resume Content:", value=extracted_text, height=300)

#     # Extract degree and domain
#     domain, degree_text = extract_degree(extracted_text)
#     st.write(f"Extracted Degree: {degree_text}")
#     st.write(f"Domain: {domain}")

#     # Convert extracted text for skill extraction
#     structured_text = ' '.join([line.replace(" ", "").lower() for line in extracted_text.split('\n') if line.strip()])

#     # Calculate skill match
#     if domain:
#         match_percentage, matching_skills = calculate_skill_match(domain, structured_text)
#         st.subheader("Matched Skills:")
#         st.write(matching_skills)
#         st.subheader("Match Percentage:")
#         st.write(f"{int(match_percentage)}%")
#     else:
#         st.write("Unable to determine the domain from the extracted degree")
