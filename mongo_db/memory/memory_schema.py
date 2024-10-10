from graphene import ObjectType, String, Boolean, Mutation, Int, Field
from memory.mongo_db.service.mongo_service import create_vector_search_index_on_collection, \
    get_vector_search_result_for_query, execute_rag_for_query_based_on_context
from memory.mongo_db.service.mongo_sample_data import load_sample_data, get_db_and_collection_for_sample_data, \
    get_vector_search_index_name_for_sample_data, get_vector_embedding_field_name_for_sample_data

from memory.mongo_db.service.mongo_sample_data import ListingSearchResultItem


class LoadSampleData(Mutation):
    ok = Boolean()
    database_name = String()
    collection_name = String()
    vector_search_index_name = String()
    vector_embedding_document_field_name = String()
    ingested_data_sample = String()

    class Arguments:
        param = String()

    def mutate(self, info, param):
        response = load_sample_data()
        return (LoadSampleData(ok=True, **response))


class CreateVectorSearchIndex(Mutation):
    ok = Boolean()

    class Arguments:
        param = String()

    def mutate(self, info, param):
        db_name, collection_name = get_db_and_collection_for_sample_data()
        vector_search_index_name = get_vector_search_index_name_for_sample_data()
        vector_embedding_field_name = get_vector_embedding_field_name_for_sample_data()
        resp = create_vector_search_index_on_collection(db_name=db_name, collection_name=collection_name,
                                                        vector_search_index_name=vector_search_index_name,
                                                        vector_embedding_field_name=vector_embedding_field_name)
        return CreateVectorSearchIndex(ok=resp)


class RunRAGQuery(Mutation):
    ok = Boolean()
    response = String()

    class Arguments:
        query = String()

    def mutate(self, info, query):
        """
        query =
            I want to stay in a place that's warm and friendly,
            and not too far from restaurants, can you recommend a place?
            Include a reason as to why you've chosen your selection.
        """
        db_name, collection_name = get_db_and_collection_for_sample_data()
        vector_search_index_name = get_vector_search_index_name_for_sample_data()
        vector_embedding_field_name = get_vector_embedding_field_name_for_sample_data()
        results = get_vector_search_result_for_query(db_name=db_name, collection_name=collection_name,
                                                     vector_search_index_name=vector_search_index_name,
                                                     vector_embedding_field_name=vector_embedding_field_name,
                                                     query=query)
        if results != {}:
            # Convert search results into a list of SearchResultItem models
            search_results_models = [
                ListingSearchResultItem(**result)
                for result in results
            ]

            search_results = [item.dict() for item in search_results_models]
            response = execute_rag_for_query_based_on_context(query=query, context=str(search_results))
        else:
            response = "No response"
        return RunRAGQuery(ok=True, response=response)


class Mutation(ObjectType):
    load_sample_data = LoadSampleData.Field()
    create_vector_search_index = CreateVectorSearchIndex.Field()
    run_rag_query = RunRAGQuery.Field()


class SampleDataListingType(ObjectType):
    database_name = String()
    collection_name = String()
    vector_search_index_name = String()
    vector_embedding_document_field_name = String()


class Query(ObjectType):
    sample_collection_detail = Field(SampleDataListingType)

    def resolve_sample_collection_detail(self, info):
        return SampleDataListingType(database_name="airbnb_dataset",
                                     collection_name="air_bnb_listings_reviews",
                                     vector_search_index_name="airbnb_text_vector_idx",
                                     vector_embedding_document_field_name="airbnb_text_embeddings")
