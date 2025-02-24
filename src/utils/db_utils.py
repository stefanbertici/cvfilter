import chromadb

def get_chroma_collection(path):
    chroma_client = chromadb.PersistentClient(path)
    return chroma_client.get_or_create_collection(
    name="my_collection",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:search_ef": 100
    })
