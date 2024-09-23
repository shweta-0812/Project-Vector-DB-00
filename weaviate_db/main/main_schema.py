import graphene
import memory.memory_schema as memory_schema


class Query(
        memory_schema.Query,
        graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass


class Mutation(
        memory_schema.Mutation,
        graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
