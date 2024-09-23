from memory.weaviate_db.db.weaviate_client import initialise_weaviate_client
from weaviate.classes.query import MetadataQuery


def vector_similarity_search(collection_name, query, limit=1, offset=0):
    wclient = initialise_weaviate_client(enable_jina=True)
    try:

        collection = wclient.collections.get(collection_name)
        response = collection.query.near_text(
            query=query,
            limit=limit,
            offset=offset,
            return_metadata=MetadataQuery(distance=True)
        )

        # for o in response.objects:
        #     print(o.properties)
        #     print(o.metadata.distance)
    finally:
        # Ensure the connection is closed
        wclient.close()
    return response
