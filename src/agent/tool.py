import os

from langchain_core.tools import tool

from src.db.MongoDB import mongo
from src.db.PineconeIndex import pinecone


@tool("mongo_filter", parse_docstring=True)
def mongo_filter(query: object, sort: list, limit: int) -> str:
    """Get a cheese data array from MongoDB.

    Args:
        query: An object containing key-value pairs for MongoDB filtering.
           - Keys for filtering MUST be from the below list of available metadata fields.
           - Values should be extracted or inferred from the user's query and the conversation history.
           - If no specific filters are discernible for any of the available fields, the "filter" object should be empty (e.g., {{}}).
           - Use only mongoDB filter expressions such as "$gt", "$in", "$ne" and "$and" as operator.
        sort: A list containing (Key, Order) pairs for sorting.
           - Keys for filtering MUST be from the below list of available metadata fields.
           - Orders must be -1 or 1
           - It has not to be empty. If it is empty, fiil with Default, [("popularity_order", 1)]
        limit:  An integer representing the number of results to retrieve.
           - Range is 1~1000.
           - The value must be enough for mongo to find the correct answer.
           - If the query asks to count all, this value must be as large as possible, i.e, 1000.
    """
    result = mongo.collection.find(query)
    if len(sort):
        result = result.sort(sort)
    result = result.limit(limit)
    result = list(result)
    return result

@tool("mongo_aggregation", parse_docstring=True)
def mongo_aggregation(pipeline: list) -> str:
    """Get a cheese data from MongoDB.

    Args:
        pipeline: A list of mongo aggregation states for aggregation.
            - Use only mongoDB aggregation expressions such as "$gt", "$group", "$unwind" and "$and" as operator.
            - This arg must make the result of mongoDB aggregation has semantic filed names such as "total_count", "num_brands".
    """
    result = mongo.collection.aggregate(pipeline)
    result = list(result)
    return result

@tool("pinecone_search", parse_docstring=True)
def pinecone_search(query: str, filter: object, limit: int) -> str:
    """Get a cheese data from Pinecone VectorDB.

    Args:
        query: Query to get data for user's query from Pinecone VectorDB.
        filter: An object containing key-value pairs for filtering.
           - Keys for filtering MUST be from the below list of available metadata fields.
           - Values should be extracted or inferred from the user's query and the conversation history.
           - If no specific filters are discernible for any of the available fields, the "filter" object should be empty (e.g., {{}}).
           - Use only pinecone metadata filter expressions as operator.
        limit : An integer representing the number of results to retrieve.
            - Range is 1~1000.
    """
    embedding = pinecone.generate_embedding(query)
    results = pinecone.indexModel.query(
        vector=embedding,
        filter=filter,
        top_k=limit,
        include_metadata=True,
        namespace=os.environ["PINECONE_ENV"]
    )
    return results.get("matches", [])