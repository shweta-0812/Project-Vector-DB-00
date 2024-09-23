# Use Weaviate vector DB to store text embeddings for search
- Uses weaviate vector DB and runs on docker using weaviate docker image
- Uses Django dev server (for development only)
- Uses Graphql for API endpoints

To run the dev server in terminal run following:
1. Go to `weaviate/db` folder
2. Rename `sample.env` to `.env` and update the values
3. Run ```poetry shell ```
4. Run ```poetry install ```
5. Run ```poetry run python manage.py runserver --settings=main.settings.dev  ```
6. Go to `http://127.0.0.1:8000/graphql`

7. Run Sample Graphql Mutation
```
mutation RunVectorDB {
  runWeaviateDb(collectionName: "questions") {
    ok
    response {
      propertyName
      propertyValue
    }
  }
}
```
8. Sample Graphql Query
```
query SampleVectorDBDetail {
    sampleCollectionDetail{
    
    collectionName,
      collectionProperties
  }
}
```
