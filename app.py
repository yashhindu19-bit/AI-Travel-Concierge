import streamlit as st
from dotenv import load_dotenv
import os
import tempfile

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_community.vectorstores import FAISS

# Load .env
load_dotenv()

# API Key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found in .env file")
    st.stop()

# Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
)

st.title("🌍 AI Travel Concierge")

uploaded_file = st.file_uploader(
    "Upload a Travel PDF",
    type=["pdf"]
)

retriever = None

if uploaded_file is not None:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        pdf_path = tmp_file.name

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=api_key,
)

    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    st.success(f"✅ PDF uploaded successfully!")
    st.success(f"Total Chunks: {len(chunks)}")

    st.subheader("First Page Preview")
    st.write(documents[0].page_content[:500])

prompt = st.chat_input("Ask your travel question...")

if prompt:

    st.chat_message("user").write(prompt)

    if retriever is None:
        st.warning("⚠ Please upload a PDF first.")
    else:

        try:

            docs = retriever.invoke(prompt)

            context = "\n\n".join(
                [doc.page_content for doc in docs]
            )

            final_prompt = f"""
You are an AI Travel Concierge.

Use ONLY the information given below.

Context:
{context}

Question:
{prompt}

If the answer is not available in the context, reply exactly:

"I could not find this information in the uploaded PDF."
"""

            response = llm.invoke(final_prompt)

            st.chat_message("assistant").write(response.content)

        except Exception as e:
            st.error(str(e))