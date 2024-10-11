import re

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ValidationError
from datasets import load_dataset
import pandas as pd
from memory.mongo_db.db.mongo_client import MongoConnection

DATASET_URI = "MongoDB/airbnb_embeddings"
DATABASE_NAME = "airbnb_dataset"
COLLECTION_NAME = "air_bnb_listings_reviews"

# MongoDB Atlas Vector Search index name
VECTOR_SEARCH_INDEX_NAME = "airbnb_text_vector_idx"
VECTOR_PRE_FILTER_SEARCH_INDEX_NAME = "airbnb_text_vector_with_filter_idx"

# NOTE: This dataset contains text and image embeddings, but we only use the text embeddings
# The field containing the text embeddings on each document within the collection
VECTOR_EMBEDDING_DOCUMENT_FIELD_NAME = "text_embeddings"


class Host(BaseModel):
    host_id: str
    host_url: str
    host_name: str
    host_location: str
    host_about: str
    host_response_time: Optional[str] = None
    host_thumbnail_url: str
    host_picture_url: str
    host_response_rate: Optional[int] = None
    host_is_superhost: bool
    host_has_profile_pic: bool
    host_identity_verified: bool


class Location(BaseModel):
    type: str
    coordinates: List[float]
    is_location_exact: bool


class Address(BaseModel):
    street: str
    government_area: str
    market: str
    country: str
    country_code: str
    location: Location


class Review(BaseModel):
    _id: str
    date: Optional[datetime] = None
    listing_id: str
    reviewer_id: str
    reviewer_name: Optional[str] = None
    comments: Optional[str] = None


class Listing(BaseModel):
    _id: int
    listing_url: str
    name: str
    summary: str
    space: str
    description: str
    neighborhood_overview: Optional[str] = None
    notes: Optional[str] = None
    transit: Optional[str] = None
    access: str
    interaction: Optional[str] = None
    house_rules: str
    property_type: str
    room_type: str
    bed_type: str
    minimum_nights: int
    maximum_nights: int
    cancellation_policy: str
    last_scraped: Optional[datetime] = None
    calendar_last_scraped: Optional[datetime] = None
    first_review: Optional[datetime] = None
    last_review: Optional[datetime] = None
    accommodates: int
    bedrooms: Optional[float] = 0
    beds: Optional[float] = 0
    number_of_reviews: int
    bathrooms: Optional[float] = 0
    amenities: List[str]
    price: int
    security_deposit: Optional[float] = None
    cleaning_fee: Optional[float] = None
    extra_people: int
    guests_included: int
    images: dict
    host: Host
    address: Address
    availability: dict
    review_scores: dict
    reviews: List[Review]
    text_embeddings: List[float]


class ListingSearchResultItem1(BaseModel):
    name: str
    accommodates: Optional[int] = None
    address: Address
    summary: Optional[str] = None
    description: Optional[str] = None
    neighborhood_overview: Optional[str] = None
    notes: Optional[str] = None


class ListingSearchResultItem2(BaseModel):
    name: str
    accommodates: Optional[int] = None
    bedrooms: Optional[int] = None
    address: Address
    space: str = None


# Note: Ensure that the  projection document in the projection stage matches the search result model.
class ListingSearchResultItem3(BaseModel):
    name: str
    accommodates: Optional[int] = None
    address: Address
    summary: Optional[str] = None
    space: Optional[str] = None
    neighborhood_overview: Optional[str] = None
    notes: Optional[str] = None
    score: Optional[float] = None


class ListingSearchResultItem4(BaseModel):
    name: str
    accommodates: Optional[int] = None
    address: Address
    averageReviewScore: Optional[float] = None
    number_of_reviews: Optional[float] = None
    combinedScore: Optional[float] = None


# NOTE: Make sure the HF_token is set in the env vars.
# NOTE: This dataset contains text and image embeddings, but this lessons only uses the text embeddings
def load_sample_data_from_huggingface():
    # load dataset
    ds = load_dataset(DATASET_URI, streaming=True, split="train")
    dataset = ds.take(100)

    # convert dataset to dataframe
    df = pd.DataFrame(dataset)

    # convert dataframe to dict
    records = df.to_dict(orient='records')

    # clean the records by setting empty values as None
    for r in records:
        for k, v in r.items():
            if isinstance(v, list):  # value is list
                r[k] = [None if pd.isnull(i) else i for i in v]
            else:
                if pd.isnull(v):
                    r[k] = None

    # after cleaning the data records dict; transform to pydantic object with defined schema
    listings = []
    try:
        # validate the records using Listing schema and transform based on the schema
        listings = [Listing(**r).dict() for r in records]
        # print(listings[0].keys())
    except ValidationError as e:
        print(e)
    return listings


def load_sample_data() -> dict:
    sample_listings_data = load_sample_data_from_huggingface()

    mclient = MongoConnection.initialise_client()
    # Pymongo client of database and collection
    db = mclient.get_database(DATABASE_NAME)
    collection = db.get_collection(COLLECTION_NAME)

    # Delete any existing records in the collection
    collection.delete_many({})

    # The ingestion process might take a few minutes
    collection.insert_many(sample_listings_data)
    print("Data ingestion into MongoDB completed")

    return {
        "database_name": DATABASE_NAME,
        "collection_name": COLLECTION_NAME,
        "vector_search_index_name": VECTOR_SEARCH_INDEX_NAME,
        "vector_embedding_document_field_name": VECTOR_EMBEDDING_DOCUMENT_FIELD_NAME,
        # "ingested_data_sample": str(sample_listings_data[0])
    }


def get_db_and_collection_for_sample_data():
    return DATABASE_NAME, COLLECTION_NAME


def get_vector_search_index_name_for_sample_data():
    return VECTOR_SEARCH_INDEX_NAME


def get_vector_embedding_field_name_for_sample_data():
    return VECTOR_EMBEDDING_DOCUMENT_FIELD_NAME


def get_pre_filter_for_sample_data():
    pass


def get_post_filter_stage_for_sample_data():
    # Specifying the metadata field to limit documents on
    search_path = "address.country"

    # Create a match stage
    match_stage = {
        "$match": {
            search_path: re.compile(r"United States"),
            "accommodates": {"$gt": 1, "$lt": 5}
        }
    }
    return match_stage


def get_projection_stage_for_sample_data():
    projection_stage = {
        "$project": {
            "_id": 0,
            "name": 1,
            "accommodates": 1,
            "address.street": 1,
            "address.government_area": 1,
            "address.market": 1,
            "address.country": 1,
            "address.country_code": 1,
            "address.location.type": 1,
            "address.location.coordinates": 1,
            "address.location.is_location_exact": 1,
            "summary": 1,
            "space": 1,
            "neighborhood_overview": 1,
            "notes": 1,
            "score": {"$meta": "vectorSearchScore"}
        }
    }
    return projection_stage


def get_average_review_score_based_document_boosting_post_filter_for_sample_data():
    average_review_score_stage = {
        "$addFields": {
            "averageReviewScore": {
                "$divide": [
                    {
                        "$add": [
                            "$review_scores.review_scores_accuracy",
                            "$review_scores.review_scores_cleanliness",
                            "$review_scores.review_scores_checkin",
                            "$review_scores.review_scores_communication",
                            "$review_scores.review_scores_location",
                            "$review_scores.review_scores_value",
                        ]
                    },
                    6  # Divide by the number of review score types to get the average
                ]
            },
            # Calculate a score boost factor based on the number of reviews
            "reviewCountBoost": "$number_of_reviews"
        }
    }

    return average_review_score_stage


def get_weighted_average_review_based_document_boosting_post_filter_for_sample_data():
    # Note: it uses the averageReviewScore and reviewCountBoost field for average calculation
    # from get_average_review_score_based_document_boosting_post_filter_for_sample_data()

    weighted_average_review_stage = {
        "$addFields": {
            "combinedScore": {
                # Formula that combines average review score and review count boost
                "$add": [
                    {"$multiply": ["$averageReviewScore", 0.9]},  # Weighted average review score
                    {"$multiply": ["$reviewCountBoost", 0.1]}  # Weighted review count boost
                ]
            }
        }
    }

    return weighted_average_review_stage


def get_sorting_based_document_boosting_post_filter_for_sample_data():
    # Note: it uses the combinedScore field for sorting
    # from get_weighted_average_review_based_document_boosting_post_filter_for_sample_data()

    # Apply the combinedScore for sorting
    sorting_stage_sort = {
        "$sort": {"combinedScore": -1}  # Descending order to boost higher combined scores
    }
    return sorting_stage_sort


def get_vector_index_pre_filters_for_sample_data():
    return {
        "accommodates": {
            "type": "number"
        },
        "bedrooms": {
            "type": "number"
        }
    }


def get_query_pre_filters_for_sample_data():
    return {
        "$and": [
            {"accommodates": {"$gte": 2}},
            {"bedrooms": {"$lte": 7}}
        ]
    }
