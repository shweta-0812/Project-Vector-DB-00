from graphene import ObjectType, String, Boolean, Mutation, List, Int, Field
from memory.weaviate_db.service.weaviate_service import create_new_weaviate_collection_with_schema, \
    load_sample_data_to_weaviate_collection, list_weaviate_collection_data, delete_weaviate_collection, \
    weaviate_vector_similarity_search, total_count_weaviate_collection_data


class CollectionProperties(ObjectType):
    property_name = String()
    property_value = String()


class RunWeaviate(Mutation):
    ok = Boolean()
    response = List(CollectionProperties)

    class Arguments:
        collection_name = String()

    def mutate(self, info, collection_name):
        # delete existing collection
        delete_weaviate_collection(collection_name=collection_name)
        # create new collection
        create_new_weaviate_collection_with_schema(collection_name=collection_name)
        # load sample data to collection
        loaded = load_sample_data_to_weaviate_collection(collection_name=collection_name)
        if loaded:
            # list data from collection and fetch only selected properties
            # response = list_weaviate_collection_data(collection_name=collection_name, properties=['question', 'answer'],
            #                                          include_vector=False)
            # print(response)
            # do a similarity search on vector DB
            response = weaviate_vector_similarity_search(collection_name=collection_name,
                                                         query="animals in movies")
        return RunWeaviate(ok=True, response=response)


class CreateCollection(Mutation):
    ok = Boolean()
    response = String()

    class Arguments:
        collection_name = String()

    # collection_name = "questions"
    def mutate(self, info, collection_name):
        delete_weaviate_collection(collection_name=collection_name)
        create_new_weaviate_collection_with_schema(collection_name=collection_name)
        loaded = load_sample_data_to_weaviate_collection(collection_name=collection_name)
        if loaded:
            resp = list_weaviate_collection_data(collection_name=collection_name, properties=['question', 'answer'],
                                                 include_vector=False)
            print(resp)
            response = weaviate_vector_similarity_search(collection_name="questions",
                                                         query="animals in movies")
        return CreateCollection(ok=True, response=response)


class DeleteCollection(Mutation):
    ok = Boolean()

    class Arguments:
        collection_name = String()

    def mutate(self, info, collection_name):
        deleted = delete_weaviate_collection(collection_name=collection_name)
        return DeleteCollection(ok=deleted)


# class LoadSampleData(Mutation):
#     ok = Boolean()
#     response = List()
#
#     class Arguments:
#         collection_name = String()
#
#     def mutate(self, info, collection_name):
#         response = []
#         loaded = load_sample_data_to_weaviate_collection(collection_name=collection_name)
#         if loaded:
#             response = list_weaviate_collection_data(collection_name=collection_name, properties=['question', 'answer'],
#                                                      include_vector=False)
#         return LoadSampleData(ok=True, response=response)
#
#
# class SearchCollection(Mutation):
#     ok = Boolean()
#     response = List()
#
#     class Arguments:
#         collection_name = String()
#         search_query = String()
#         limit = Int()
#
#     # query = "animals in movies"
#     def mutate(self, info, collection_name, search_query, limit):
#         response = weaviate_vector_similarity_search(collection_name=collection_name,
#                                                      search_query=search_query, limit=limit)
#         return SearchCollection(ok=True, response=response)
#
#

# class ListCollection(Mutation):
#     ok = Boolean()
#     data_list = List()
#     data_size = Int()
#     total_size = Int()
#
#     class Arguments:
#         collection_name = String()
#         properties = List()
#         limit = Int()
#
#     # properties=["category"]
#     def mutate(self, info, collection_name, properties, limit):
#         data_list = list_weaviate_collection_data(collection_name=collection_name, properties=properties,
#                                                   limit=limit)
#         data_size = len(data_list)
#         total_size = total_count_weaviate_collection_data(collection_name=collection_name)
#
#         return SearchCollection(ok=True, data_size=data_size, data_list=data_list, total_size=total_size)

class Mutation(ObjectType):
    run_weaviate_db = RunWeaviate.Field()
    create_weaviate_db_collection = CreateCollection.Field()
    delete_weaviate_db_collection = DeleteCollection.Field()
    # load_sample_data_to_weaviate_db_collection = LoadSampleData.Field()
    # search_weaviate_db_collection = SearchCollection.Field()
    # list_weaviate_db_collection_objects = ListCollection.Field()


class SampleCollectionDetailType(ObjectType):
    collection_name = String()
    collection_properties = List(String)


class Query(ObjectType):
    sample_collection_detail = Field(SampleCollectionDetailType)

    def resolve_sample_collection_detail(self, info):
        return SampleCollectionDetailType(collection_name="questions",
                                          collection_properties=["question", "answer", "category"])
