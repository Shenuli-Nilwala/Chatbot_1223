from google import genai 
from google.genai import types 
import pathlib 
import streamlit as st
import base64

# Function to set background
def set_bg_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Page config
st.set_page_config(page_title="Chatbot", layout="wide")

# Set background (use full path if needed)
set_bg_local("macro-1.jpg")

client = genai.Client(api_key="AIzaSyB44_iR4THIU0_oLs0RqT7YnAUBGbHqqBc")

# Retrieve and encode the PDF byte
filepath = pathlib.Path('data_1.pdf')
def generateResponse(question):
    prompt = question
    response = client.models.generate_content(model="gemini-2.5-flash",contents=[types.Part.from_bytes(data=filepath.read_bytes(),mime_type='application/pdf',),prompt])
    return response.text
st.set_page_config(page_title="Chatbot", layout="wide") 
st.title("Welcome to the  Chat Bot")
st.write("Ask me anything related to uploaded PDF")

# Initialize chat history 
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history 
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your question here...") 
if user_input: 
    # Display user message 
    st.session_state.messages.append({"role": "user", "content":user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        # Get chatbot response using RAG
        bot_response = generateResponse(user_input)
        
        # Display bot response
        st.session_state.messages.append({"role": "assistant", "content":bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)