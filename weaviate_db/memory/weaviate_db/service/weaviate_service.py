from memory.weaviate_db.db.weaviate_client import create_weaviate_client
from memory.weaviate_db.models.weaviate_query import delete_collection, create_collection_with_schema, aggregate_over_collection, load_sample_data_using_jinaai_embedding_model
from memory.weaviate_db.search.weaviate_search import vector_similarity_search
from memory.weaviate_db.models.weaviate_query import list_collection_objects
from memory.weaviate_db.db.weaviate_schemas import SCHEMAS
from common_utils import sample_data_download

def check_client():
    meta_data = create_weaviate_client()
    return meta_data


def create_new_weaviate_collection_with_schema(collection_name):
    return create_collection_with_schema(collection_name=collection_name, schema=SCHEMAS[collection_name])


def delete_weaviate_collection(collection_name):
    return delete_collection(collection_name=collection_name)


def load_sample_data_to_weaviate_collection(collection_name):
    file_name = "jeopardy_tiny_with_vectors_all-OpenAI-ada-002.json"  # This file includes pre-generated vectors
    url = f"https://raw.githubusercontent.com/weaviate-tutorials/quickstart/main/data/{file_name}"

    data = sample_data_download(url=url)

    weaviate_data_obj_list = []
    for i, d in enumerate(data):
        weaviate_obj = {
            "answer": d["Answer"],
            "question": d["Question"],
            "category": d["Category"],
        }
        weaviate_data_obj_list.append(weaviate_obj)

    return load_sample_data_using_jinaai_embedding_model(collection_name=collection_name, weaviate_data_obj_list=weaviate_data_obj_list )




'''
Vector search returns the objects with most similar vectors to that of the query.
'''


def weaviate_vector_similarity_search(collection_name, search_query, limit=1):
    result = []
    query_return = vector_similarity_search(collection_name=collection_name, query=search_query, limit=limit)
    for o in query_return.objects:
        result.append(o.properties)
    return result


def list_weaviate_collection_data(collection_name, properties, include_vector=False, limit=1, offset=0):
    result = []
    query_return = list_collection_objects(collection_name, properties, include_vector=include_vector, limit=limit,
                                           offset=offset)
    for o in query_return:
        result.append(o.properties)
    return result


def total_count_weaviate_collection_data(collection_name):
    aggregate_return = aggregate_over_collection(collection_name=collection_name)
    return aggregate_return.total_count
