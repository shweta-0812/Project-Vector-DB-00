import weaviate
from dotenv import load_dotenv, find_dotenv
# import openai
from common_utils import get_env_key

_ = load_dotenv(find_dotenv())  # read local .env file

WEAVIATE_API_KEY = get_env_key('WEAVIATE_API_KEY')
WEAVIATE_DB_HOST = get_env_key('WEAVIATE_DB_HOST')
WEAVIATE_DB_PORT = get_env_key('WEAVIATE_DB_PORT')
WEAVIATE_DB_HTTP_SECURE = get_env_key('WEAVIATE_DB_HTTP_SECURE')
WEAVIATE_DB_GRPC_HOST = get_env_key('WEAVIATE_DB_GRPC_HOST')
WEAVIATE_DB_GRPC_PORT = get_env_key('WEAVIATE_DB_GRPC_PORT')
WEAVIATE_DB_GRPC_SECURE = get_env_key('WEAVIATE_DB_GRPC_SECURE')
WEAVIATE_API_KEY = get_env_key('WEAVIATE_API_KEY')

# OPENAI_API_KEY = get_env_key('OPENAI_API_KEY')
# OPENAI_API_BASE_URL = get_env_key('OPENAI_API_BASE_URL')

JINA_API_KEY = get_env_key('JINA_API_KEY')

# openai.api_key = OPENAI_API_KEY


def initialise_weaviate_client(enable_jina=False, enable_openai=False):
    headers = {}
    # if enable_openai:
    #     headers["X-OpenAI-Api-Key"] = OPENAI_API_KEY
    #     headers["X-OpenAI-BaseURL"] = OPENAI_API_BASE_URL
    if enable_jina:
        headers["X-Jinaai-Api-Key"] = JINA_API_KEY

    return weaviate.connect_to_custom(
        http_host=WEAVIATE_DB_HOST,
        http_port=WEAVIATE_DB_PORT,
        http_secure=WEAVIATE_DB_HTTP_SECURE,
        grpc_host=WEAVIATE_DB_GRPC_HOST,
        grpc_port=WEAVIATE_DB_GRPC_PORT,
        grpc_secure=WEAVIATE_DB_GRPC_SECURE,
        auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
        headers=headers

    )


'''
Create an embedded instance of Weaviate vector database
JINA is enabled for creating text embeddings
'''


def create_weaviate_client(enable_jina=True, enable_openai=False):
    wclient = initialise_weaviate_client(enable_jina=enable_jina, enable_openai=enable_openai)
    try:
        print(f"Client created? {wclient.is_ready()}")
        meta_data = wclient.get_meta()
    finally:
        # Ensure the connection is closed
        wclient.close()
    return meta_data
