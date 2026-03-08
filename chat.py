from google import genai 
from google.genai import types 
import pathlib 
import streamlit as st 
client = genai.Client(api_key="GEMINI_API_KEY")

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