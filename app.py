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
# STREAMLIT CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Travel Concierge",
    page_icon="🌍",
    layout="wide"
)


# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main-title {
    text-align: center;
    font-size: 46px;
    font-weight: 800;
    margin-bottom: 5px;
}

.main-subtitle {
    text-align: center;
    font-size: 19px;
    margin-bottom: 25px;
}

.hero {
    padding: 35px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 25px;
}

.feature-card {
    padding: 22px;
    border-radius: 16px;
    border: 1px solid rgba(128,128,128,0.25);
    min-height: 150px;
    margin-bottom: 15px;
}

.feature-card h3 {
    margin-bottom: 8px;
}

.feature-card p {
    font-size: 14px;
    opacity: 0.8;
}

.section-title {
    font-size: 28px;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 15px;
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")


# =====================================================
# API KEY CHECK
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
# SQLITE DATABASE
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


def save_search(query):

    cursor.execute(
        """
        INSERT INTO search_history(query)
        VALUES(?)
        """,
        (query,)
    )

    conn.commit()


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
# GEMINI
# =====================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3,
)


# =====================================================
# TAVILY
# =====================================================

tavily = TavilyClient(
    api_key=TAVILY_API_KEY
)


# =====================================================
# WEB SEARCH
# =====================================================

def web_search(query):

    try:

        result = tavily.search(
            query=query,
            max_results=3
        )

        return str(result)

    except Exception as e:

        return f"Web search error: {e}"


# =====================================================
# WEATHER SEARCH
# =====================================================

def weather_search(city):

    url = (
        "https://api.openweathermap.org/"
        "data/2.5/weather"
    )

    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
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
🌤️ **Weather Information**

**City:** {data['name']}

🌡️ **Temperature:** {data['main']['temp']} °C

☁️ **Weather:** {data['weather'][0]['description']}

💧 **Humidity:** {data['main']['humidity']} %
"""

    except Exception as e:

        return f"❌ Weather error: {e}"


# =====================================================
# HOTEL SEARCH
# =====================================================

def hotel_search(city):

    try:

        # Find city in India

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


        # Search hotels

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
            f"## 🏨 Hotels in "
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
# ITINERARY GENERATOR
# =====================================================

def generate_itinerary(
    city,
    days
):

    prompt = f"""
Create a practical {days}-day travel itinerary
for {city}.

For each day include:

### Day X
- Morning activities
- Afternoon activities
- Evening activities
- Popular attractions
- Local food suggestions

Keep the plan clear, practical and easy to follow.

Do not invent exact ticket prices or opening hours.
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
# LANGCHAIN TOOLS
# =====================================================

web_tool = Tool(
    name="web_search",
    func=web_search,
    description=(
        "Search latest travel information "
        "from the internet."
    )
)


weather_tool = Tool(
    name="weather_search",
    func=weather_search,
    description=(
        "Get current weather information "
        "for a city."
    )
)


hotel_tool = Tool(
    name="hotel_search",
    func=hotel_search,
    description=(
        "Search hotels in any city."
    )
)


# =====================================================
# BASE AGENT
# =====================================================

base_tools = [
    web_tool,
    weather_tool,
    hotel_tool,
]

base_agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an AI Travel Concierge.

You have access to these tools:

1. Web Search
   - Use for latest travel information,
     attractions, hotels, visas, etc.

2. Weather Search
   - Use for current weather
     of any city.

3. Hotel Search
   - Use for finding hotels
     in a city.

Give clear, practical and useful
travel answers.

If a tool is needed, use the
appropriate tool before answering.
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

base_agent = create_tool_calling_agent(
    llm=llm,
    tools=base_tools,
    prompt=base_agent_prompt,
)

base_agent_executor = AgentExecutor(
    agent=base_agent,
    tools=base_tools,
    verbose=True,
)


# =====================================================
# AUTO SCROLL HELPER
# =====================================================

def auto_scroll_to_answer():
    st.components.v1.html(
        """
        <script>
        setTimeout(function() {
            try {
                window.parent.scrollTo({
                    top: document.body.scrollHeight,
                    behavior: "smooth"
                });
            } catch (e) {
                window.scrollTo({
                    top: document.body.scrollHeight,
                    behavior: "smooth"
                });
            }
        }, 300);
        </script>
        """,
        height=0,
    )


# =====================================================
# SIDEBAR NAVIGATION
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

    st.markdown(
        '<div class="hero">'
        '<div class="main-title">🌍 AI Travel Concierge</div>'
        '<div class="main-subtitle">'
        'Your intelligent travel companion'
        '</div>'
        '<p>Plan smarter • Explore better • Travel easier</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # -------------------------------------------------
    # HOME SEARCH BAR
    # -------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🔎 Where do you want to go?'
        '</div>',
        unsafe_allow_html=True
    )

    home_query = st.text_input(
        "Ask anything about your trip",
        placeholder="e.g. Best places to visit in Manali",
        key="home_search"
    )

    

    if st.button(
        "✨ Search with AI",
        key="home_search_button"
    ):

        if home_query.strip():

            save_search(home_query)

            with st.spinner(
                "Finding the best travel information..."
            ):

                try:

                    response = base_agent_executor.invoke(
                        {
                            "input": home_query
                        }
                    )

                    answer = response.get(
                        "output",
                        ""
                    )

                    st.divider()

                    st.subheader(
                        "🤖 AI Travel Assistant"
                    )

                    if answer:

                        st.markdown(answer)
                        auto_scroll_to_answer()

                    else:

                        st.warning(
                            "⚠️ The AI returned an empty answer."
                        )

                except Exception as e:

                    st.error(
                        f"❌ Assistant error: {e}"
                    )

        else:

            st.warning(
                "Please enter a travel question."
            )


    st.divider()

    st.markdown(
        '<div class="section-title">'
        '✈️ Everything You Need for Your Trip'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🏨 Hotel Search</h3>
                <p>
                Find hotels in your destination
                with our travel search tool.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🌤️ Live Weather</h3>
                <p>
                Check current weather conditions
                for your destination.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🔎 Travel Search</h3>
                <p>
                Get useful and latest travel
                information from the web.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown(
            """
            <div class="feature-card">
                <h3>📄 PDF Assistant</h3>
                <p>
                Upload a travel guide and ask
                questions from your document.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col5:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🗺️ AI Itinerary</h3>
                <p>
                Generate practical day-by-day
                travel plans using AI.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col6:
        st.markdown(
            """
            <div class="feature-card">
                <h3>📜 Search History</h3>
                <p>
                Easily view your previous
                travel searches.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


    st.divider()

    st.success(
        "✨ Your AI Travel Concierge is ready!"
    )

    st.info(
        "💡 Use the search bar above for a quick answer, "
        "or choose **Travel Assistant** for PDF and itinerary features."
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


    # =================================================
    # PDF UPLOAD
    # =================================================

    st.divider()

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


    # =================================================
    # CREATE TOOLS
    # =================================================

    tools = [
        web_tool,
        weather_tool,
        hotel_tool
    ]


    # =================================================
    # PDF PROCESSING
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


        # Embeddings

        embeddings = (
            GoogleGenerativeAIEmbeddings(
                model="gemini-embedding-001",
                google_api_key=GEMINI_API_KEY
            )
        )


        # Vector Store

        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings
        )


        # Retriever

        retriever = vectorstore.as_retriever(
            search_kwargs={
                "k": 3
            }
        )


        # PDF Search

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


        # PDF Tool

        pdf_tool = Tool(
            name="pdf_search",
            func=pdf_search,
            description=(
                "Search information from "
                "the uploaded travel PDF."
            )
        )


        tools.append(
            pdf_tool
        )


        st.success(
            "✅ PDF uploaded successfully!"
        )

        st.write(
            f"**Total Chunks:** {len(chunks)}"
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

    agent_prompt = ChatPromptTemplate.from_messages(
        [

            (
                "system",

                """
You are an AI Travel Concierge.

You have access to these tools:

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

Give clear and useful answers.
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
        prompt=agent_prompt,
    )


    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
    )


    # =================================================
    # ITINERARY
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

                itinerary = generate_itinerary(
                    destination,
                    days
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
    # CHAT
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


                answer = response.get(
                    "output",
                    ""
                )


                with st.chat_message(
                    "assistant"
                ):

                    if answer:

                        st.markdown(
                            answer
                        )

                        auto_scroll_to_answer()

                    else:

                        st.warning(
                            "⚠️ The AI returned "
                            "an empty answer."
                        )


            except Exception as e:

                with st.chat_message(
                    "assistant"
                ):

                    st.error(
                        f"❌ Assistant error: {e}"
                    )


# =====================================================
# SEARCH HISTORY PAGE
# =====================================================

elif page == "📜 Search History":

    st.markdown(
        '<div class="main-title">📜 Search History</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subtitle">'
        'Your recent travel searches'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    history = get_history()

    if history:

        st.info(
            f"🔎 You have {len(history)} saved searches."
        )

        for i, (query, created_at) in enumerate(history):

            st.markdown(
                f"""
                <div class="feature-card">
                    <h4>🔎 {query}</h4>
                    <p>🕒 {created_at}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.info(
            "📭 No search history found yet."
        )             