
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def get_embedding_model():
    """Load the embedding model once and reuse it."""

    global _model

    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)
        print("Embedding model loaded successfully!")

    return _model


def create_embedding_text(chunk):
    """Prepare code and context for embedding generation."""

    return f"""
Repository: {chunk.get('repository', '')}
File: {chunk.get('file_path', '')}
Language: {chunk.get('language', '')}
Type: {chunk.get('type', '')}
Name: {chunk.get('name', '')}
Parent class: {chunk.get('parent_class') or 'None'}

Code:
{chunk.get('code', '')}
""".strip()


def generate_embeddings(chunks):
    """Generate vector embeddings for code chunks."""

    if not chunks:
        return []

    model = get_embedding_model()

    texts = [create_embedding_text(chunk) for chunk in chunks]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return embeddings.tolist()