import streamlit as st
import os
import tempfile
import requests
import asyncio
import sqlite3

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from dotenv import load_dotenv

from tavily import TavilyClient
from langchain_core.tools import Tool

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

from langchain.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)


# =====================================================
# Load Environment Variables
# =====================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")


# =====================================================
# SQLite Database
# =====================================================

conn = sqlite3.connect(
    "travel.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


# =====================================================
# API Key Checks
# =====================================================

if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY not found.")
    st.stop()

if not TAVILY_API_KEY:
    st.error("❌ TAVILY_API_KEY not found.")
    st.stop()

if not WEATHER_API_KEY:
    st.error("❌ OPENWEATHER_API_KEY not found.")
    st.stop()

if not GEOAPIFY_API_KEY:
    st.error("❌ GEOAPIFY_API_KEY not found.")
    st.stop()


# =====================================================
# Gemini LLM
# =====================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3,
)


# =====================================================
# Tavily Client
# =====================================================

tavily = TavilyClient(
    api_key=TAVILY_API_KEY
)


# =====================================================
# Web Search Function
# =====================================================

def web_search(query):

    try:

        result = tavily.search(
            query=query,
            max_results=3
        )

        return str(result)

    except Exception as e:

        return str(e)


# =====================================================
# Weather Search Function
# =====================================================

def weather_search(city):

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        data = response.json()

        if response.status_code != 200:

            return data.get(
                "message",
                "City not found"
            )

        return f"""
🌤️ Weather Information

City: {data['name']}

🌡️ Temperature: {data['main']['temp']} °C

☁️ Weather: {data['weather'][0]['description']}

💧 Humidity: {data['main']['humidity']} %
"""

    except Exception as e:

        return str(e)


# =====================================================
# Hotel Search Function
# =====================================================

def hotel_search(city):

    try:

        # Step 1: Find city in India

        geo_url = (
            "https://api.geoapify.com/"
            "v1/geocode/search"
        )

        geo_params = {

            "text": city,

            "type": "city",

            "filter": "countrycode:in",

            "limit": 1,

            "apiKey": GEOAPIFY_API_KEY
        }

        geo_response = requests.get(
            geo_url,
            params=geo_params,
            timeout=10
        )

        geo_data = geo_response.json()

        if not geo_data.get("features"):

            return (
                f"❌ Could not find "
                f"{city} in India."
            )

        location = (
            geo_data["features"][0]["properties"]
        )

        lat = location["lat"]
        lon = location["lon"]


        # Step 2: Search hotels

        hotel_url = (
            "https://api.geoapify.com/v2/places"
        )

        hotel_params = {

            "categories":
                "accommodation.hotel",

            "filter":
                f"circle:{lon},{lat},25000",

            "limit": 10,

            "apiKey":
                GEOAPIFY_API_KEY
        }

        hotel_response = requests.get(
            hotel_url,
            params=hotel_params,
            timeout=10
        )

        hotel_data = hotel_response.json()

        if not hotel_data.get("features"):

            return (
                f"❌ No hotels found "
                f"in {city}."
            )


        result = (
            f"🏨 Hotels in "
            f"{city.title()}\n\n"
        )

        for place in hotel_data["features"]:

            props = place["properties"]

            name = props.get(
                "name",
                "Hotel"
            )

            address = props.get(
                "formatted",
                "Address not available"
            )

            result += (
                f"🏨 **{name}**\n"
                f"📍 {address}\n\n"
            )

        return result


    except Exception as e:

        return (
            f"❌ Hotel search error: {e}"
        )


# =====================================================
# Save Search
# =====================================================

def save_search(query):

    cursor.execute(
        """
        INSERT INTO search_history(query)
        VALUES(?)
        """,
        (query,)
    )

    conn.commit()


# =====================================================
# Get Search History
# =====================================================

def get_history():

    cursor.execute(
        """
        SELECT query, created_at
        FROM search_history
        ORDER BY id DESC
        """
    )

    return cursor.fetchall()


# =====================================================
# AI Itinerary Generator
# =====================================================

def generate_itinerary(
    city,
    days
):

    prompt = f"""
Create a practical {days}-day
travel itinerary for {city}.

For each day include:

- Morning activities
- Afternoon activities
- Evening activities
- Popular attractions
- Local food suggestions

Keep the plan clear and easy to follow.

Do not invent exact ticket prices
or opening hours.
"""

    try:

        response = llm.invoke(
            prompt
        )

        return response.content

    except Exception as e:

        return (
            f"❌ Unable to generate "
            f"itinerary: {e}"
        )


# =====================================================
# LangChain Tools
# =====================================================

web_tool = Tool(
    name="web_search",
    func=web_search,
    description=(
        "Search latest travel "
        "information from the internet."
    )
)


weather_tool = Tool(
    name="weather_search",
    func=weather_search,
    description=(
        "Get current weather "
        "information for a city."
    )
)


hotel_tool = Tool(
    name="hotel_search",
    func=hotel_search,
    description=(
        "Search hotels in any city."
    )
)


tools = [
    web_tool,
    weather_tool,
    hotel_tool,
]


# =====================================================
# Streamlit Page Configuration
# =====================================================

st.set_page_config(
    page_title="AI Travel Concierge",
    page_icon="🌍",
    layout="wide"
)


# =====================================================
# Sidebar Navigation
# =====================================================

with st.sidebar:

    st.header("🧭 Navigation")

    page = st.radio(
        "Choose a section:",
        [
            "🏠 Home",
            "💬 Travel Assistant",
            "📜 Search History"
        ]
    )


# =====================================================
# HOME PAGE
# =====================================================

if page == "🏠 Home":

    st.title(
        "🌍 Welcome to AI Travel Concierge"
    )

    st.caption(
        "Your AI-powered personal travel assistant."
    )

    st.markdown(
        """
        ### ✈️ What can you do?

        - 🏨 Search hotels
        - 🌤️ Check current weather
        - 🔎 Search travel information
        - 📄 Ask questions from travel PDFs
        - 🗺️ Generate AI travel itineraries
        - 📜 View your search history
        """
    )

    st.info(
        "💡 Select **Travel Assistant** "
        "from the sidebar to start "
        "planning your trip."
    )

    st.divider()

    st.success(
        "✅ AI Travel Concierge is ready!"
    )


# =====================================================
# TRAVEL ASSISTANT PAGE
# =====================================================

elif page == "💬 Travel Assistant":

    st.title(
        "💬 Travel Assistant"
    )

    st.caption(
        "Ask about hotels, weather, "
        "destinations, itineraries, "
        "or your uploaded travel PDF."
    )

    st.info(
        "💡 Try: 'Find hotels in Delhi', "
        "'Weather in Jaipur', or "
        "'Best places to visit in Manali'."
    )

    st.divider()


    # =================================================
    # PDF UPLOAD
    # =================================================

    st.subheader(
        "📄 Travel Guide"
    )

    st.caption(
        "Upload a travel guide PDF to "
        "get answers directly from "
        "your document."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help=(
            "Upload your travel guide "
            "in PDF format."
        ),
        key="travel_pdf"
    )


    retriever = None
    pdf_tool = None


    # =================================================
    # PROCESS PDF
    # =================================================

    if uploaded_file is not None:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp_file:

            tmp_file.write(
                uploaded_file.getvalue()
            )

            pdf_path = tmp_file.name


        # Load PDF

        loader = PyPDFLoader(
            pdf_path
        )

        documents = loader.load()


        # Split PDF

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = splitter.split_documents(
            documents
        )


        # Gemini Embeddings

        embeddings = (
            GoogleGenerativeAIEmbeddings(
                model="gemini-embedding-001",
                google_api_key=GEMINI_API_KEY
            )
        )


        # FAISS Vector Store

        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings
        )


        # Retriever

        retriever = (
            vectorstore.as_retriever(
                search_kwargs={
                    "k": 3
                }
            )
        )


        # =============================================
        # PDF SEARCH FUNCTION
        # =============================================

        def pdf_search(query):

            docs = retriever.invoke(
                query
            )

            if not docs:

                return (
                    "No relevant information "
                    "found in the uploaded PDF."
                )

            return "\n\n".join(
                doc.page_content
                for doc in docs
            )


        # =============================================
        # PDF TOOL
        # =============================================

        pdf_tool = Tool(
            name="pdf_search",
            func=pdf_search,
            description=(
                "Search information from "
                "the uploaded travel PDF."
            )
        )


        if pdf_tool not in tools:

            tools.append(
                pdf_tool
            )


        st.success(
            "✅ PDF uploaded successfully!"
        )

        st.write(
            f"**Total Chunks:** "
            f"{len(chunks)}"
        )

        st.subheader(
            "📄 PDF Preview"
        )

        st.write(
            documents[0]
            .page_content[:700]
        )


    # =================================================
    # CREATE AGENT
    # =================================================

    prompt = ChatPromptTemplate.from_messages(
        [

            (
                "system",

                """
You are an AI Travel Concierge.

You have access to the following tools:

1. Web Search
   - Use for latest travel information,
     attractions, hotels, visas, etc.

2. Weather Search
   - Use for current weather
     of any city.

3. Hotel Search
   - Use for finding hotels
     in a city.

4. PDF Search
   - Use whenever the answer can
     be found in the uploaded
     travel PDF.

Always choose the best tool
before answering.

If no tool is required,
answer normally.
"""
            ),

            (
                "human",
                "{input}"
            ),

            MessagesPlaceholder(
                variable_name="agent_scratchpad"
            ),
        ]
    )


    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )


    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
    )


    # =================================================
    # AI ITINERARY GENERATOR
    # =================================================

    st.divider()

    st.subheader(
        "🗺️ AI Itinerary Generator"
    )

    col1, col2 = st.columns(2)


    with col1:

        destination = st.text_input(
            "📍 Destination",
            placeholder="e.g. Jaipur",
            key="itinerary_destination"
        )


    with col2:

        days = st.number_input(
            "📅 Number of Days",
            min_value=1,
            max_value=15,
            value=3,
            key="itinerary_days"
        )


    if st.button(
        "✨ Generate Itinerary",
        key="generate_itinerary_button"
    ):

        if destination.strip():

            with st.spinner(
                "Creating your itinerary..."
            ):

                itinerary = (
                    generate_itinerary(
                        destination,
                        days
                    )
                )


            st.success(
                "✅ Itinerary generated!"
            )

            st.markdown(
                itinerary
            )


            save_search(
                f"Itinerary: "
                f"{destination} - "
                f"{days} days"
            )


            st.download_button(
                label="📥 Download Itinerary",
                data=itinerary,
                file_name=(
                    f"{destination}_"
                    f"itinerary.txt"
                ),
                mime="text/plain",
                key="download_itinerary"
            )


        else:

            st.warning(
                "Please enter a destination."
            )


    # =================================================
    # CHAT INTERFACE
    # =================================================

    st.divider()

    st.subheader(
        "💬 Ask Your Travel Question"
    )

    user_input = st.chat_input(
        "Ask your travel question..."
    )


    if user_input:

        save_search(
            user_input
        )


        st.chat_message(
            "user"
        ).write(
            user_input
        )


        with st.spinner(
            "Thinking..."
        ):

            try:

                response = (
                    agent_executor.invoke(
                        {
                            "input": user_input
                        }
                    )
                )


                with st.chat_message(
                    "assistant"
                ):

                    st.markdown(
                        response["output"]
                    )


            except Exception as e:

                st.error(
                    f"❌ {e}"
                )


# =====================================================
# SEARCH HISTORY PAGE
# =====================================================

elif page == "📜 Search History":

    st.title(
        "📜 Search History"
    )

    history = get_history()


    if history:

        for query, created_at in history:

            st.markdown(
                f"🕒 **{created_at}**"
            )

            st.write(
                f"🔍 {query}"
            )

            st.divider()


    else:

        st.info(
            "No search history found."
        )