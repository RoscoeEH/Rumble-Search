import os

from llama_index.core import Document, VectorStoreIndex, StorageContext, load_index_from_storage, Settings
from llama_index.readers.file.docs.base import PDFReader
from llama_index.readers.file import MarkdownReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter, MarkdownNodeParser
from llama_index.core.vector_stores import SimpleVectorStore

from local_paths import BASE_INDEX_DIR

embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-mpnet-base-v2")
Settings.embed_model = embed_model

def get_index(index_name, chunk_size=512, base_dir=BASE_INDEX_DIR):
    index_dir = os.path.join(base_dir, index_name)
    os.makedirs(index_dir, exist_ok=True)

    if os.path.exists(index_dir) and os.listdir(index_dir):
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        index = load_index_from_storage(storage_context, embed_model=embed_model)
    else:
        vector_store = SimpleVectorStore()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        splitter = SentenceSplitter(chunk_size=chunk_size)
        index = VectorStoreIndex(
            nodes=[],
            storage_context=storage_context,
            node_parser=splitter,
            embed_model=embed_model
        )
        index.storage_context.persist(persist_dir=index_dir)
    
    # Store persistent directory
    index._persist_dir = index_dir
    return index

def update_docs_metadata(docs, file_name, file_path):
    for doc in docs:
        doc.doc_id = file_name
        if doc.metadata is None:
            doc.metadata = {}
        doc.metadata.update({
            "file_name": file_name,
            "file_path": file_path,
        })

def ingest_files_to_index(index, directory):
    # Get existing doc ids
    existing_doc_ids = set(index.ref_doc_info.keys())

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        # Skip directories
        if not os.path.isfile(file_path):
            continue

        # Skip already indexed files
        if file_name in existing_doc_ids:
            continue

        ext = os.path.splitext(file_name)[1].lower()

        try:
            if ext == ".pdf":
                reader = PDFReader()
                docs = reader.load_data(file_path)
                update_docs_metadata(docs, file_name, file_path)

                splitter = SentenceSplitter()
                nodes = splitter.get_nodes_from_documents(docs)

            elif ext == ".md":
                reader = MarkdownReader()
                docs = reader.load_data(file_path)
                update_docs_metadata(docs, file_name, file_path)

                parser = MarkdownNodeParser()
                nodes = parser.get_nodes_from_documents(docs)

            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                # txt's have different metadata
                doc = Document(
                    text=text,
                    doc_id=file_name,
                    metadata={
                        "file_name": file_name,
                        "file_path": file_path,
                    },
                )

                splitter = SentenceSplitter()
                nodes = splitter.get_nodes_from_documents([doc])

            # Load to index
            for node in nodes:
                # Fixed metadata bug, do not remove
                node.metadata = node.metadata or {}
                node.metadata.update({
                    "file_name": file_name,
                    "file_path": file_path,
                })
                index.insert(node)

        except Exception as e:
            print(f"ERROR: Failed to process {file_name}: {e}")

    persist_dir = getattr(index, '_persist_dir', None)
    if persist_dir:
        index.storage_context.persist(persist_dir=persist_dir)
    else:
        index.storage_context.persist()
        print("WARNING: Persist directory not found. Using default")
