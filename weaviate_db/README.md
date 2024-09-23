# Use Weaviate vector DB to store text embeddings for search
- Uses weaviate vector DB and runs on docker using weaviate docker image
- Uses Django dev server (for development only)
- Uses Graphql for API endpoints

Sample Graphql Mutation
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

Sample Graphql Query
```
query SampleVectorDBDetail {
    sampleCollectionDetail{
    
    collectionName,
      collectionProperties
  }
}
```
