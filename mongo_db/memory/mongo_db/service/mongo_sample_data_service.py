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


class ListingSearchResultItem(BaseModel):
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


def get_post_filter_additional_stages_for_sample_data():
    # Specifying the metadata field to limit documents on
    search_path = "address.country"

    # Create a match stage
    match_stage = {
        "$match": {
            search_path: re.compile(r"United States"),
            "accommodates": {"$gt": 1, "$lt": 5}
        }
    }

    additional_stages = [match_stage]
    return additional_stages


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
