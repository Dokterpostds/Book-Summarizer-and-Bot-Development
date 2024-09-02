import os
from datetime import datetime
from typing import Dict, Optional
from llama_index.llms.openai import OpenAI
from src.global_settings import get_paths
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
# from llama_index.core.extractors import SummaryExtractor
from llama_index.embeddings.openai import OpenAIEmbedding
from src.logging import ActionLogger
from src.metadata import Metadata

class Uploader:
    def __init__(self, references : Dict[str, Optional[str]]):
        self.theme = references["Theme"]
        self.title = references["Title"]
        self.paths = get_paths(self.theme, self.title)
        self.metadata = Metadata(references)
        self.logger = ActionLogger(self.theme, self.title)

    def ingest_documents(self):
        """Load documents from the storage path."""
        storage_path = self.paths["STORAGE_PATH"]
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        
        documents = SimpleDirectoryReader(
            storage_path, 
            filename_as_id=True
        ).load_data()

        for doc in documents:
            print(doc.id_)
            self.logger.log_action(
                f"File '{doc.id_}' uploaded by user", 
                action_type="UPLOAD"
            )

        return documents

    def process_documents(self):
        # Ingest documents
        print("test")
        documents = self.ingest_documents()
        print("documents")

        # Get metadata
        documents_with_metadata = self.metadata.apply_metadata(documents)
        print("documents_with_metadata")

        # Initialize cache
        cache_path = self.paths["CACHE_FILE"]
        if os.path.exists(cache_path):
            try:
                cached_hashes = IngestionCache.from_persist_path(cache_path)
                print("Cache file found. Running using cache...")
                self.logger.log_action("Cache file found and loaded.", action_type="CACHE")
            except Exception as e:
                print(f"Error loading cache: {str(e)}. Running without cache...")
                self.logger.log_action(f"Error loading cache: {str(e)}. Proceeding without cache.", action_type="CACHE")
                cached_hashes = None
        else:
            print("No cache file found. Running without cache...")
            self.logger.log_action("No cache file found, proceeding without cache.", action_type="CACHE")
            cached_hashes = None

        # Set up the ingestion pipeline
        pipeline = IngestionPipeline(
            transformations=[
                TokenTextSplitter(
                    chunk_size=1024, 
                    chunk_overlap=20
                ),
                OpenAIEmbedding()
            ],
            cache=cached_hashes
        )

        # Run the pipeline
        # try:
        nodes = pipeline.run(documents=documents_with_metadata)

        # Add metadata to nodes
        node_metadata = {
            "processed_at": str(datetime.now()),
            "pipeline_stage": "PostProcessing",
        }
        nodes_with_metadata = self.metadata.add_metadata(nodes, node_metadata)

        pipeline.cache.persist(cache_path)
        self.logger.log_action("Pipeline processing completed and cache updated.", action_type="PROCESS")
        # except Exception as e:
        #     self.logger.log_action(f"Pipeline processing failed: {str(e)}", action_type="ERROR")
        #     raise e
        
        return nodes_with_metadata