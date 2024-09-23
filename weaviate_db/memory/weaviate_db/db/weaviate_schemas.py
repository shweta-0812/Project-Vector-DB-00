# Set the vectorizer to "text2vec-openai" to use the OpenAI API for text vectorization
# Set the vectorizer to "text2vec_jinaai" to use the JINA API for text vectorization

SCHEMAS = {
    'questions': {
        "vectorizer": "text2vec_jinaai",
        "properties": [
            {"name": "question",
             "data_type": "text"},
            {"name": "answer",
             "data_type": "text"},
            {"name": "category",
             "data_type": "text"}

        ]
    }
}
