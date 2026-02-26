import os

from llama_index.core import Document, VectorStoreIndex, StorageContext, load_index_from_storage, Settings
from llama_index.readers.file.docs.base import PDFReader
from llama_index.readers.file import MarkdownReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter, MarkdownNodeParser
from llama_index.core.vector_stores import SimpleVectorStore

BASE_INDEX_DIR = "./indexes"

embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-mpnet-base-v2")
Settings.embed_model = embed_model

def get_index(index_name, chunk_size=512, base_dir=BASE_INDEX_DIR):
    index_dir = os.path.join(base_dir, index_name)
    os.makedirs(index_dir, exist_ok=True)

    vector_store_path = os.path.join(index_dir, "default__vector_store.json")
    
    if os.path.exists(vector_store_path):
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
    
    return index


def ingest_files_to_index(index: VectorStoreIndex, directory):
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if not os.path.isfile(file_path):
            continue
        if index.get_node_by_doc_id(file_name) is not None:
            continue

        ext = os.path.splitext(file_name)[1].lower()

        if ext == ".pdf":
            reader = PDFReader()
            docs = reader.load_data(file_path)
            splitter = SentenceSplitter()
            nodes = splitter.get_nodes_from_documents(docs)
        elif ext == ".md":
            reader = MarkdownReader()
            docs = reader.load_data(file_path)
            parser = MarkdownNodeParser()
            nodes = parser.get_nodes_from_documents(docs)
        else:
            text = open(file_path, "r", encoding="utf-8").read()
            doc = Document(text=text, doc_id=file_name, metadata={"file_name": file_name, "file_path": file_path})
            splitter = SentenceSplitter()
            nodes = splitter.get_nodes_from_documents([doc])

        for node in nodes:
            index.insert(node)

    index.storage_context.persist()
