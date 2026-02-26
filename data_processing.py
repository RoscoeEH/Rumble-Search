import os
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.schema import Document
from llama_index.text_splitter import TokenTextSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from manage_index import BASE_INDEX_DIR

# Configure embedding model
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-mpnet-base-v2")

def get_index(index_name: str, chunk_size: int = 512, chunk_overlap: int = 50, base_dir: str = BASE_INDEX_DIR):
    index_dir = os.path.join(base_dir, index_name)
    os.makedirs(index_dir, exist_ok=True)

    storage_context = StorageContext.from_defaults(persist_dir=index_dir)
    
    try:
        index = load_index_from_storage(storage_context)
    except Exception:
        text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        index = VectorStoreIndex(
            nodes=[],
            storage_context=storage_context,
            text_splitter=text_splitter,
            embed_model=embed_model  # local GPU embeddings
        )
    return index


def ingest_files_to_index(index: VectorStoreIndex, directory: str):
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if not os.path.isfile(file_path):
            continue

        # Skip files already indexed
        if index.get_node_by_doc_id(file_name) is not None:
            continue

        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Create a Document with metadata
        doc = Document(
            text=content,
            doc_id=file_name,
            metadata={
                "file_name": file_name,
                "file_path": file_path
            }
        )

        # Insert doc
        index.insert(doc)

    # Dave
    index.storage_context.persist()
