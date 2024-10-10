from memory.mongo_db.vector_search.mongo_vector_search import index_vector_embeddings, run_vs_for_query

from memory.mongo_db.db.mongo_client import MongoConnection

from llm.openai.service.llm_service import generate_llm_response


def get_mongo_db_and_collection_conn(db_name: str, collection_name: str):
    mclient = MongoConnection.initialise_client()

    # Pymongo client of database and collection
    db_conn = mclient.get_database(db_name)
    collection_conn = db_conn.get_collection(collection_name)

    return db_conn, collection_conn


def create_vector_search_index_on_collection(db_name: str,
                                             collection_name: str,
                                             vector_search_index_name: str,
                                             vector_embedding_field_name: str
                                             ):
    _, collection_conn = get_mongo_db_and_collection_conn(db_name=db_name, collection_name=collection_name)
    return index_vector_embeddings(collection_conn=collection_conn,
                                   vector_search_index_name=vector_search_index_name,
                                   vector_embedding_field_name=vector_embedding_field_name
                                   )


def get_vector_search_result_for_query( query: str,
                                        db_name: str,
                                        vector_search_index_name: str,
                                        vector_embedding_field_name: str,
                                        collection_name: str) -> dict:
    db_conn, collection_conn = get_mongo_db_and_collection_conn(db_name=db_name, collection_name=collection_name, )
    results = run_vs_for_query(query=query, db=db_conn,
                               collection=collection_conn,
                               vector_index=vector_search_index_name,
                               text_embedding_field=vector_embedding_field_name)
    return results if results else {}


def execute_rag_for_query_based_on_context(query: str, context: str) -> str:
    response = generate_llm_response(query=query, context=context)
    return response
