from manage_index import update_indexes, INDEX_MAP
from retreiver import query_indexes

import argparse
from your_index_file import INDEX_MAP, query_indexes  # adjust import


def update_indexes():
    for name, index_obj in INDEX_MAP.items():
        print(f"Updating index: {name}")
        index_obj.update()


def run_query(query, index_name, top_k):
    print(f"Query: {query}")
    print(f"Index: {index_name}")
    print()

    results = query_indexes(index_name, query, top_k=top_k)

    for i, node in enumerate(results):
        print(f"\nResult {i + 1}:")
        
        if hasattr(node, "score"):
            print(f"Score: {node.score}")

        if hasattr(node, "metadata"):
            metadata = node.metadata

            if "file_name" in metadata:
                print(f"File: {metadata['file_name']}")

            if "file_path" in metadata:
                print(f"Path: {metadata['file_path']}")

        if hasattr(node, "text"):
            print(node.text)
        elif hasattr(node, "get_text"):
            print(node.get_text())

def list_indexes():
    print(f"Indexes:")
    for i, name in enumerate(INDEX_MAP.keys()):
        print(name)

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
    if args.query:
        run_query(
            query=args.query,
            index_name=args.index,
            top_k=args.top_k
        )

    if args.list:
        list_indexes()

    else:
        print("No action specified. Try -h or --help")


if __name__ == "__main__":
    main()
