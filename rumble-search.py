from manage_index import update_indexes, INDEX_MAP
from retreiver import query_indexes
import argparse

OUTPUT = "./output.txt"

def update_indexes():
    for name, index_obj in INDEX_MAP.items():
        index_obj.update()


def run_query(query, index_name, top_k):
    if top_k > 32:
        return f"ERROR: Cannot display more that 32 results\n"

    try:
        results = query_indexes(index_name, query, top_k=top_k)
    except ValueError:
        return f"ERROR: The index '{index_name}' does not exist\n"

    output_str = ""
    output_str += f"Query: {query}\n"
    output_str += f"Index: {index_name}\n\n"
    
    for i, node in enumerate(results):
        output_str += f"Result {i + 1}:\n"
        
        if hasattr(node, "score"):
            output_str += f"Score: {node.score}\n"

        if hasattr(node, "metadata"):
            metadata = node.metadata

            if "file_name" in metadata:
                output_str += f"File: {metadata['file_name']}\n"

            if "file_path" in metadata:
                output_str += f"Path: {metadata['file_path']}\n"

        if hasattr(node, "text"):
            output_str += node.text + '\n'
        elif hasattr(node, "get_text"):
            output_str += node.get_text() + '\n'
    return output_str

def list_indexes():
    output_str = "Indexes:\n"
    for i, name in enumerate(INDEX_MAP.keys()):
        output_str += f"{i + 1}) {name}\n"
    return output_str
        

def main():
    parser = argparse.ArgumentParser(description="Index CLI")

    # Flags
    parser.add_argument(
        "-u", "--update",
        action="store_true",
        help="Update all indexes"
    )

    parser.add_argument(
        "-q", "--query",
        type=str,
        help="Query string"
    )

    parser.add_argument(
        "-i", "--index",
        type=str,
        default="all",
        help="Index name"
    )

    parser.add_argument(
        "-k", "--top_k",
        type=int,
        default=10,
        help="Number of results to return"
    )

    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all indexes"
    )

    args = parser.parse_args()

    # update
    if args.update:
        update_indexes()

    # query
    elif args.query:
        out = run_query(
            query=args.query,
            index_name=args.index,
            top_k=args.top_k
        )
        with open(OUTPUT, "w") as f:
            f.write(out)

    elif args.list:
        out = list_indexes()
        with open(OUTPUT, "w") as f:
            f.write(out)

    else:
        print("No action specified. Try -h or --help")


if __name__ == "__main__":
    main()
