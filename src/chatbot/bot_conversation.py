import os
import json
import streamlit as st
from llama_index.llms.openai import OpenAI
from llama_index.core import load_index_from_storage, StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.storage.chat_store import SimpleChatStore
from src.global_settings import get_paths
from interface.bot_ui import ChatInterface

class ChatStoreManager:
    def __init__(self, theme, title):
        self.paths = get_paths(theme, title)
        self.chat_store = self.load_chat_store()
    
    def load_chat_store(self):
        try:
            return SimpleChatStore.from_persist_path(self.paths["CONVERSATION_FILE"])
        except FileNotFoundError:
            return SimpleChatStore()
    
    def persist_chat_store(self):
        # Define the path from self.paths dictionary
        convert_dict = self.paths["CONVERSATION_FILE"]

        self.chat_store.persist(self.paths["CONVERSATION_FILE"])
        print(f"File has already been persisted: {convert_dict}")

    # def add_message(self, role, content, timestamp):
    #     self.chat_store.add_message(key=role, message=content)
    
    def add_message(self, messages):
        return(self.chat_store.add_message(key ='0', message= messages))

    def get_messages(self):
        return self.chat_store.get_messages(key="0")

    def clear_chat_store(self):
        self.chat_store.delete_messages(key="0")
        self.persist_chat_store()

    def delete_chat_store_file(self):
        if os.path.exists(self.paths["CONVERSATION_FILE"]):
            os.remove(self.paths["CONVERSATION_FILE"])    

class ChatBot:
    def __init__(self, user_name, chat_store_manager, references):
        self.user_name = user_name
        self.chat_store_manager = chat_store_manager
        self.theme = references["Theme"]
        self.title = references["Title"]
        paths = get_paths(self.theme, self.title)
        self.storage_context = StorageContext.from_defaults(
            persist_dir=paths["INDEX_STORAGE"]
        )
        self.agent = self.initialize_chatbot()


    def initialize_chatbot(self):
        
        memory = ChatMemoryBuffer.from_defaults(
            token_limit=3000, 
            chat_store=self.chat_store_manager.chat_store, 
            chat_store_key="0"
        )

        index = load_index_from_storage(self.storage_context, index_id="vector")
        
        study_materials_engine = index.as_query_engine(similarity_top_k=3)

        study_materials_tool = QueryEngineTool(
            query_engine=study_materials_engine,
            metadata=ToolMetadata(
                name="study_materials",
                description=(
                    f"Provides official information about "
                    f"{self.title}. Use a detailed plain "
                    f"text question as input to the tool."
                ),
            )
        )
        
        print("Metadata : ", study_materials_tool.metadata)

        return OpenAIAgent.from_tools(
            tools=[study_materials_tool],
            llm=OpenAI(model="gpt-4o-mini"),
            memory=memory,
            system_prompt=(
                f"""Anda adalah sebuah bot belajar, seorang tutor pribadi. 
                Tujuan Anda adalah untuk membantu {self.user_name} belajar dan lebih memahami materi di buku: {self.title}. 
                Jika pertanyaan tersebut tidak termasuk dalam alat ini, cukup kembalikan dengan mengatakan bahwa Anda tidak tahu jawabannya dan katakan jika materi tidak ada dibuku, silahkan tanya pertanyaan terkait {self.theme}. 
                Silakan ajukan pertanyaan terkait dengan Ortopedi. Jawablah dengan bahasa Indonesia tanpa mengubah istilah kedokteran"""
            )
        )

    def get_response(self, prompt):
        return str(self.agent.chat(prompt))  
    
    def get_sources(self, prompt):
        index = load_index_from_storage(self.storage_context, index_id="vector")
        retriever = index.as_retriever(similarity_top_k=3)
        # Retrieve the top 3 similar documents along with their metadata
        results = retriever.retrieve(prompt)
        metadata = []
        # Extract the metadata
        for result in results:
            score = result.score
            if result.score > 0.75 :
                metadata = result.node.metadata  # Metadata is stored in extra_info
                print(f"Metadata: {metadata}") 
            print(f"Score: {score}")
        llm=OpenAI(model="gpt-4o-mini")
        if metadata :    
            source = llm.complete(f"""Generate APA-formatted references using the provided metadata. If there are multiple sets of metadata with different titles or authors, generate separate references for each. Ensure that page numbers are included in the references. If a book has multiple pages specified, list them all. The output should be formatted as follows:

            Reference:

            Author(s). (Year). *Title of the book*. Publisher. pp. Page numbers
            
            Given Metadata:
            {metadata}
            """
            )
        else :
            source = ""
        return source
          

