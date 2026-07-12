import streamlit as st
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# .env file load karo
load_dotenv()

# API key lo
api_key = os.getenv("GEMINI_API_KEY")

# Gemini model initialize karo
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key
)

st.title("AI Travel Concierge")

if prompt := st.chat_input("Apna travel question pucho..."):
    st.chat_message("user").write(prompt)

    response = llm.invoke(prompt)

    st.chat_message("assistant").write(response.content)