import time
from pymongo.operations import SearchIndexModel

from vectorizer.openai.service.openai_service import get_embedding


def print_query_stats(db, collection, pipeline):
    explain_query_execution = db.command(  # sends a database command directly to the MongoDB server
        'explain', {  # return information about how MongoDB executes a query or command without actually running it
            'aggregate': collection.name,  # specifies the name of the collection on which the aggregation is performed
            'pipeline': pipeline,  # the aggregation pipeline to analyze
            'cursor': {}  # indicates that default cursor behavior should be used
        },
        verbosity='executionStats')  # detailed statistics about the execution of each stage of the aggregation pipeline

    vector_search_explain = explain_query_execution['stages'][0]['$vectorSearch']
    millis_elapsed = vector_search_explain['explain']['collectStats']['allCollectorStats']['millisElapsed']

    print(f"Total time for the execution to complete on the database server: {millis_elapsed} milliseconds")


def get_vs_index_model(vector_search_index_name: str, vector_embedding_field_name: str, filters: dict):
    vs_index_model = SearchIndexModel(
        definition={
            "mappings": {  # describes how fields in the database documents are indexed and stored
                "dynamic": False,  # do not automatically index new fields that appear in the document
                "fields": {  # properties of the fields that will be indexed.
                    vector_embedding_field_name: {
                        "dimensions": 1536,  # size of the vector.
                        "similarity": "cosine",  # algorithm used to compute the similarity between vectors
                        "type": "knnVector",  # selection of similar vectors: KNN Algo
                    },
                    **filters
                },
            }
        },
        name=vector_search_index_name,  # identifier for the vector search index
    )

    return vs_index_model


def create_vs_index(collection_conn, vector_search_index_name: str, vector_search_index_model: dict) -> bool:
    # Check if the index already exists
    index_exists = False
    for index in collection_conn.list_indexes():
        # print(index['name'])
        if index['name'] == vector_search_index_name:
            index_exists = True
            break

    # Create the index if it doesn't exist
    if not index_exists:
        try:
            result = collection_conn.create_search_index(model=vector_search_index_model)
            print("Creating index...")
            time.sleep(20)  # add 20 sec sleep to ensure vector index has compeleted inital sync before utilization
            print("Wait a few minutes before conducting search with index to ensure index intialization")
            print("Index created successfully:", result)
            return True
        except Exception as e:
            print(f"Error creating vector search index: {str(e)}")
            return False
    else:
        print(f"Index '{vector_search_index_name}' already exists.")
        return False


def run_vs_for_query(db, collection,
                     query: str,
                     vector_index: str,
                     text_embedding_field: str,
                     additional_stages: list = [],
                     filters: dict = {},
                     limit: int = 20, ):
    """
    Perform a vector search in the MongoDB collection based on the user query.

    Args:
    user_query (str): The user's query string.
    db (MongoClient.database): The database object.
    collection (MongoCollection): The MongoDB collection to search.
    additional_stages (list): Additional aggregation stages to include in the pipeline.

    Returns:
    list: A list of matching documents.
    """
    # Generate embedding for the user query
    # since the dataset text is embedded using Openai text-embedding model we need to use the same model
    # for query text
    query_embedding = get_embedding(query)

    if query_embedding is None:
        return "Invalid query or embedding generation failed."

    # Define the vector search stage using $vectorSearch Operator
    vector_search_stage = {
        "$vectorSearch": {
            "index": vector_index,  # specifies the index to use for the search
            "queryVector": query_embedding,  # the vector representing the query
            "path": text_embedding_field,  # field in the documents containing the vectors to search against
            "numCandidates": 150,  # number of candidate matches to consider
            "limit": limit,
            "filter": filters,
        }
    }

    # Define the aggregate pipeline with the vector search stage and additional stages
    pipeline = [vector_search_stage] + additional_stages
    print("Execute the search")

    # Execute the search using aggregate framework
    results = collection.aggregate(pipeline)
    # print(list(results))

    # Optional step
    print_query_stats(db=db, collection=collection, pipeline=pipeline)

    return list(results)


def index_vector_embeddings(collection_conn,
                            vector_search_index_name: str,
                            vector_embedding_field_name: str,
                            vector_index_pre_filters: dict = {}) -> bool:
    """
    vector_search_index_name:  MongoDB Atlas Vector Search index name
    vector_embedding_field_name:  The field containing the text embeddings on each document
    vector_index_pre_filters: The filters to be added at the time index creation

    Creates an index of vector embeddings based on the vector embeddings present in vector embedding field of the
    document inside the Mongo collection
    """

    vector_search_index_model = get_vs_index_model(vector_search_index_name=vector_search_index_name,
                                                   vector_embedding_field_name=vector_embedding_field_name,
                                                   filters=vector_index_pre_filters)
    return create_vs_index(collection_conn=collection_conn,
                           vector_search_index_name=vector_search_index_name,
                           vector_search_index_model=vector_search_index_model)
