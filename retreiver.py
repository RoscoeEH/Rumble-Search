from manage_index import INDEX_MAP

def query_indexes(index_name, query, top_k):
    # One index
    if index_name != "all":
        if index_name not in INDEX_MAP:
            raise ValueError(f"Index '{index_name}' not found.")
        
        retriever = INDEX_MAP[index_name].retrieve_index().as_retriever(
            similarity_top_k=top_k
        )
        return retriever.retrieve(query)

    # Search all
    all_results = []

    for name, index_obj in INDEX_MAP.items():
        retriever = index_obj.retrieve_index().as_retriever(
            similarity_top_k=top_k
        )
        results = retriever.retrieve(query)
        all_results.extend(results)

    # re-rank
    try:
        def get_score(node):
            if hasattr(node, "score"):
                return node.score
            return 0

        all_results = sorted(all_results, key=get_score, reverse=True)
        
    except Exception:
        pass

    return all_results[:top_k]
