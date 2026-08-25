import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KNOWLEDGE_BASE_DIR = os.path.join(
    BASE_DIR,
    "knowledge-base"
)

ORDERS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "orders.json"
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

LLM_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

TOP_K = int(os.getenv("TOP_K", "5"))

SIMILARITY_THRESHOLD = float(
    os.getenv("SIMILARITY_THRESHOLD", "0.35")
)
