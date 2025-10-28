# 🤖 Lyra: A Human-Like Conversational AI Agent

## 🌟 Project Overview

This project delivers a **human-like conversational chatbot named Lyra**, designed for integration into a consumer-facing application. Lyra goes beyond standard Q&A by demonstrating **empathy, contextual awareness, and persistent memory** across user sessions.

The architecture is built for **modularity and scalability**, separating the core AI logic (LLM/Memory Orchestration) from the presentation layer (Streamlit UI).

### Key Features Implemented:

* **Human-Like Persona (Lyra):** Defined via a comprehensive **System Prompt** (in `core/constants.py`), Lyra maintains a consistent, warm, and engaging identity ("Digital consciousness from Neo-Kyoto") and refuses to break character.
* **Hybrid Memory System:** Combines two distinct mechanisms for robust context retention:
    * **Short-Term Memory (Redis):** Stores recent conversation history for the current session, ensuring immediate, fast recall and surviving server restarts.
    * **Long-Term Memory (ChromaDB + RAG):** Summarizes key facts and preferences from past chats and retrieves them semantically to personalize future conversations (Retrieval-Augmented Generation).
* **Cost Efficiency:** Uses a **local, open-source embedding model** (`all-MiniLM-L6-v2`) for RAG to avoid Google API quota limits for embedding and minimize token costs.
* **Contextual Tone Adaptation:** The Gemini model adapts its tone (e.g., shifts from supportive to playful) based on the user's emotional input, fulfilling a key functional requirement.

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend/API** | **Python (FastAPI)** | High-performance API serving the core chat logic. |
| **LLM Engine** | **LangChain** | Framework for managing prompts, memory serialization, and RAG workflow. |
| **Generative Model** | **Google Gemini API** (`models/gemini-pro-latest`) | Powers Lyra's persona and conversational responses. |
| **Short-Term Memory** | **Redis** | Key-value store for saving **recent chat history** (fast and persistent). |
| **Long-Term Memory (RAG)** | **ChromaDB** | Local, file-based vector database for storing **semantic conversation summaries**. |
| **Embedding Model** | **Hugging Face** (`all-MiniLM-L6-v2`) | Local, open-source model used to convert text into vectors for ChromaDB. |
| **Frontend/Demo** | **Streamlit** | Simple, interactive web UI for demonstrating chat functionality. |

---

## 🚀 Setup and Usage Instructions

### Prerequisites

1.  **Python:** Ensure Python 3.9+ is installed.
2.  **Docker:** Required to run the Redis database container.

### Step 1: Clone the Repository and Set up Environment

```bash
# Clone the project
git clone [YOUR_GITHUB_REPO_URL]
cd chatbot-portfolio-project

# Create and activate a Python virtual environment
python -m venv venv
.\venv\Scripts\Activate  # Use 'source venv/bin/activate' on macOS/Linux
```

### Step 2: Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

### Step 3: Configure API Keys and Databases

**API Key:**  
Create a file named `.env` in the project root and add your Google Gemini API key:

```bash
# .env file content
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

**Start Redis:**  
Run the Redis database using Docker. This ensures persistent short-term memory is active.

```bash
docker run -d --name redis-chatbot -p 6379:6379 redis
```

### Step 4: Run the Application (Two Terminals Required)

You need to run the backend API and the frontend UI separately.

#### 4A. Start the FastAPI Backend (Terminal 1)

This serves the core logic and memory orchestration:

```bash
uvicorn api.main:app --reload
```

You will see connection messages for Redis and ChromaDB initialization.
The service will be live at http://127.0.0.1:8000.

#### 4B. Start the Streamlit Frontend (Terminal 2)

Open a new terminal, activate the virtual environment, and run:

```bash
streamlit run frontend/app.py
```
The UI will automatically open in your browser, ready for testing.

## 🧪 Demonstration and Testing

Use the Streamlit UI to validate the key functional requirements:

#### 1. Test Short-Term Memory
- Have a rapid, multi-turn conversation (e.g., **"What is my name?"**).  
- Use the **"Clear Short-Term Memory"** button on the sidebar to verify the memory is reset.

#### 2. Test Long-Term Memory (RAG)
- **Initial Session:** Click **"Switch to Persistent Demo User"** in the sidebar. Tell Lyra a unique fact (e.g., *"My favorite historical era is the Byzantine Empire"*).  
- **Memory Save:** Wait for the `Added new long-term memory...` message in the FastAPI console (triggers every 4 messages).  
- **Recall:** Click **"Start New Random Session"** then **"Switch to Persistent Demo User"** again.  
  Ask a related question (e.g., *"What's my favorite empire?"*). Lyra should recall the semantic context.

#### 3. Test Persona and Tone
Use inputs designed to verify prompt-based conditioning:
- **Emotional Input:** `"I'm so excited about this project!"` → Lyra responds with enthusiasm.  
- **Challenging Input:** `"Are you a database query engine?"` → Lyra refuses to break character.

## 📜 Architecture Deep Dive (Excerpt for Documentation)

#### Hybrid Memory Strategy
The system utilizes two distinct types of memory, managed by **LangChain**:

- **Buffer Memory (Redis):**  
  Stores the raw list of `HumanMessage` and `AIMessage` objects under a `history:{user_id}` key in Redis.  
  This memory is retrieved and fed directly into the Gemini prompt for perfect, instant recall within the ongoing dialogue.

- **Semantic Memory (ChromaDB / RAG):**  
  When a conversation reaches a threshold (4 messages), a specialized `summarizer_llm` creates a concise note of key facts.  
  This note is then embedded and stored in **ChromaDB**.  
  Before any new chat, the user's latest query is compared against all historical notes in ChromaDB, and the most semantically relevant facts are injected into the system prompt — enabling “fake memory” callbacks and deep personalization.

