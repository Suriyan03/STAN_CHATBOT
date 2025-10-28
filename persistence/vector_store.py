# File: persistence/vector_store.py

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables (though not strictly needed here anymore)
load_dotenv()

# --- THE FIX IS HERE ---
# Initialize a free, open-source embedding model that runs locally.
# The first time this runs, it will download the model files (a few hundred MB).
print("Initializing local embedding model...")
embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
print("Local embedding model loaded.")

# Initialize the LangChain Chroma vector store with the local model.
vector_store = Chroma(
    persist_directory="./db",
    embedding_function=embedding_function
)

print("ChromaDB using local embeddings is ready.")