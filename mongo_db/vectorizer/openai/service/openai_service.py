import openai

from common_utils import get_env_key

OPENAI_API_KEY = get_env_key('OPENAI_API_KEY')


def get_embedding(text):
    openai.api_key = OPENAI_API_KEY

    """Generate an embedding for the given text using OpenAI's API."""

    # Check for valid input
    if not text or not isinstance(text, str):
        return None

    try:
        # Call OpenAI API to get the embedding
        embedding = openai.embeddings.create(
            input=text,
            model="text-embedding-3-small", dimensions=1536).data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error in get_embedding: {e}")
        return None
