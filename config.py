from pathlib import Path


BASE_DIR = Path(__file__).parent

DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
CHROMA_DIR = BASE_DIR / "data" / "chroma"
FEEDBACK_DIR = BASE_DIR / "data" / "feedback"

COLLECTION_NAME = "novamart_knowledge_base"

EMBEDDING_MODEL = "text-embedding-3-small"
GENERATION_MODEL = "gpt-5"

CHUNK_SIZE = 180
CHUNK_OVERLAP = 40

TOP_K = 4

MAX_QUESTION_LENGTH = 1000
MAX_UPLOAD_SIZE_MB = 2
MAX_HISTORY_MESSAGES = 6

SUPPORTED_FILE_TYPES = {
    ".txt",
    ".md",
    ".pdf",
}