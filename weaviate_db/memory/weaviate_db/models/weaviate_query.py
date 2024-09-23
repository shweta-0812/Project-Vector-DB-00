from weaviate.classes.config import Configure, Property, DataType
from memory.weaviate_db.db.weaviate_client import initialise_weaviate_client


def delete_collection(collection_name):
    wclient = initialise_weaviate_client()
    deleted = False
    try:
        # CAUTION: This will delete your collection
        if wclient.collections.exists(collection_name):
            wclient.collections.delete(collection_name)
            deleted = True
    finally:
        # Ensure the connection is closed
        wclient.close()
    return deleted


def create_collection_with_schema(collection_name, schema):
    # create a collection
    # define properties
    # define a vectorizer

    wclient = initialise_weaviate_client()
    try:
        if not wclient.collections.exists(collection_name):
            # create properties
            properties = []
            for p in schema["properties"]:
                if p["data_type"] == "text":
                    data_type = DataType.TEXT

                properties.append(Property(
                    name=p["name"],
                    data_type=data_type
                ))

            match schema["vectorizer"]:
                case "text2vec-openai":
                    vectorizer_config = Configure.Vectorizer.text2vec_openai()
                case "text2vec_jinaai":
                    vectorizer_config = Configure.Vectorizer.text2vec_jinaai()
                case _:
                    vectorizer_config = None

            collection = wclient.collections.create(
                name=collection_name,
                vectorizer_config=vectorizer_config,
                # vectorizer_config=[
                #     Configure.NamedVectors.text2vec_jinaai(
                #         name="question_vector",
                #         source_properties=["question"]
                #     )
                # ],
                # properties=[
                #     Property(name="question", data_type=DataType.TEXT),
                #     Property(name="answer", data_type=DataType.TEXT),
                #     Property(name="category", data_type=DataType.TEXT),
                # ]
                properties=properties
            )
            print(collection.config.get(simple=False))
    finally:
        # Ensure the connection is closed
        wclient.close()
    return True


def load_sample_data_using_jinaai_embedding_model(collection_name, weaviate_data_obj_list):
    wclient = initialise_weaviate_client(enable_jina=True)
    loaded_data = []
    try:
        collection = wclient.collections.get(collection_name)
        with collection.batch.dynamic() as batch:
            for weaviate_obj in weaviate_data_obj_list:
                # The model provider integration will automatically vectorize the object
                l = batch.add_object(
                    properties=weaviate_obj,
                    # vector=vector  # Optionally provide a pre-obtained vector embeddings for the texts in the obj
                )
                loaded_data.append(l)

        print(collection.batch.failed_objects)
    finally:
        # Ensure the connection is closed
        wclient.close()
        return loaded_data


def list_collection_objects(collection_name, properties, include_vector=False, limit=1, offset=0):
    wclient = initialise_weaviate_client()
    try:
        collection = wclient.collections.get(collection_name)
        response = collection.query.fetch_objects(
            return_properties=properties,
            limit=limit,
            offset=offset,
            include_vector=include_vector,
        )
    finally:
        # Ensure the connection is closed
        wclient.close()

    # for o in response.objects:
    #     print(o.properties)
    #     print(o.vector["default"])

    return response.objects


def aggregate_over_collection(collection_name):
    wclient = initialise_weaviate_client()
    try:
        collection = wclient.collections.get(collection_name)
        aggregate_return = collection.aggregate.over_all(total_count=True)
        # collection = wclient.collections.get(collection_name)
        # for item in collection.iterator():
        #     print(item.uuid, item.properties)

    finally:
        wclient.close()
    return aggregate_return
