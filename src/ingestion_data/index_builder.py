from llama_index.core import VectorStoreIndex, TreeIndex, load_index_from_storage
from llama_index.core import StorageContext
from src.global_settings import get_paths
from llama_index.llms.openai import OpenAI
import os
import json

class IndexManager:
    def __init__(self, theme, title=None):
        self.theme = theme
        self.title = title
        self.paths = get_paths(theme, title) if title else None
        self.index_directory = os.path.join(self.paths["INDEX_STORAGE"]) if self.paths else None
        self.llm = OpenAI(model="gpt-4o-mini", max_tokens=1000)
        self.vector_index = None
        self.tree_index = None

    def build_indexes(self, nodes):
        try:
            storage_context = StorageContext.from_defaults(
                persist_dir=self.index_directory
            )
            self.vector_index = load_index_from_storage(
                storage_context, index_id="vector"
            )
            self.tree_index = load_index_from_storage(
                storage_context, index_id="tree"
            )
            print("All indices loaded from storage.")
        except Exception as e:
            print(f"Error occurred while loading indices")
            storage_context = StorageContext.from_defaults()
            self.vector_index = VectorStoreIndex(
                nodes, storage_context=storage_context
            )
            self.vector_index.set_index_id("vector")
            self.tree_index = TreeIndex(
                nodes, storage_context=storage_context, llm=self.llm
            )
            self.tree_index.set_index_id("tree")
            storage_context.persist(
                persist_dir=self.index_directory
            )
            
            print("New indexes created and persisted.")
        return self.vector_index, self.tree_index


class IndexMerger:
    def __init__(self, theme, title):
        self.theme = theme
        self.paths = get_paths(theme, title) if title else None

    def get_titles_for_theme(self):
        titles_dir =  get_paths["BOOK_TITLES"]
        json_file_path = os.path.join(titles_dir, "list_title.json")
                # Load the existing list from JSON file if it exists
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as file:
                list_title = json.load(file)
        titles = [ref['Title'] for ref in list_title if ref.get('Theme') == self.theme]
        
        if not titles:
            raise ValueError(f"No titles found for the topic '{self.theme}'")
        
        return titles

    def merge_indices(self):
        titles = self.get_titles_for_theme()
        
        vector_nodes = []
        tree_nodes = []
        vector_indices = []
        tree_indices = []
        
        for title in titles:
            path = f"database/index_storage/{self.theme}/{title}/"
            storage_context = StorageContext.from_defaults(persist_dir=path)
            
            try:
                vector_index = load_index_from_storage(
                    storage_context, index_id="vector"
                )
                tree_index = load_index_from_storage(
                    storage_context, index_id="tree"
                )
                
                vector_store_dict = vector_index.storage_context.vector_store.to_dict()
                embedding_dict = vector_store_dict['embedding_dict']
                for doc_id, vector_node in vector_index.storage_context.docstore.docs.items():
                    # necessary to avoid re-calc of embeddings
                    vector_node.embedding = embedding_dict[doc_id]
                    vector_nodes.append(vector_node)
                
                tree_store_dict = tree_index.storage_context.tree_store.to_dict()
                embedding_dict = tree_store_dict['embedding_dict']
                for doc_id, tree_node in tree_index.storage_context.docstore.docs.items():
                    # necessary to avoid re-calc of embeddings
                    tree_node.embedding = embedding_dict[doc_id]
                    tree_nodes.append(tree_node)    
                                    
                vector_indices.append(vector_index)
                tree_indices.append(tree_index)
            except Exception as e:
                print(f"Error loading indices for title '{title}': {e}")
        
        merge_path = self.paths["MERGE_PATH"]
        merge_storage_context = StorageContext.from_defaults(persist_dir=merge_path)
        if vector_nodes:
            merged_vector_index = VectorStoreIndex(node=vector_nodes, storage_context=merge_storage_context)
            merged_vector_index.set_index_id("vector")

        if tree_indices:
            merged_tree_index = TreeIndex(node=tree_nodes, storage_context=merge_storage_context)
            merged_tree_index.set_index_id("tree")
            print("Tree indices merged and saved.")
         
        merge_storage_context.persist(
            persit_dir=merge_path
        )    
        
        return merged_vector_index, merged_tree_index