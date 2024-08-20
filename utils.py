from sentence_transformers import SentenceTransformer
import pinecone
import google.generativeai as genai
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# Configure the Google Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the GenAI model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Pinecone

pc = pinecone.Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))

# Assuming you have an index named 'your_index'
index = pc.Index("langchain-chatbot2")
def find_match(input):
    input_em = model.encode(input).tolist()
    result = index.query(input_em, top_k=2, includeMetadata=True)
    return result['matches'][0]['metadata']['text'] + "\n" + result['matches'][1]['metadata']['text']

def query_refiner(conversation, query):
    # Create a prompt string
    prompt = (f"Given the following user query and conversation log, "
              f"formulate a question that would be the most relevant to provide the user "
              f"with an answer from a knowledge base.\n\nCONVERSATION LOG: \n{conversation}\n\n"
              f"Query: {query}\n\nRefined Query:")
    
    # Generate the refined query using Gemini AI
    response = model.predict(prompt)
    
    return response

def get_conversation_string():
    conversation_string = ""
    for i in range(len(st.session_state['responses'])-1):
        conversation_string += "Human: " + st.session_state['requests'][i] + "\n"
        conversation_string += "Bot: " + st.session_state['responses'][i+1] + "\n"
    return conversation_string
