import streamlit as st
from io import BytesIO
import os
from llama_index.core import TreeIndex, load_index_from_storage
from llama_index.core.storage import StorageContext 
from llama_index.llms.openai import OpenAI
from src.global_settings import get_paths
from src.ingestion_data.document_uploader import Uploader
from src.preprocessing.parsing import parse_topics_to_dict
from src.extractor import Extractor
from langchain_openai import ChatOpenAI
from jinja2 import Template
from src.prompt import (
    human_topic_explanation_template,
    human_sub_topic_explanation_template,
    system_summarize_template,
    human_summarize_template
)
from src.summarizer.summarization import SummarizationDeck, Summarizer

class SummarizeGenerator:
    def __init__(self, content_table:BytesIO, references):
        self.content_table = content_table
        self.theme = references["Theme"]
        self.title = references["Title"]
        self.references = references
        self.paths = get_paths(self.theme, self.title)
        self.llm = OpenAI(temperature=0.2, model="gpt-4o-mini", max_tokens=4096)
        self.uploader = Uploader(references)
        self.client = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.extractor = Extractor(self.client)    

    def load_documents(self):
        with st.spinner("Loading documents..."):
            st.info("Docs loaded!")
            
    def _extract_topic(self): 
        try: 
            topic_extractor, token_usage = self.extractor.topic_extractor(self.content_table)
            topic_dict = dict(parse_topics_to_dict(topic_extractor))

            return topic_dict
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return e

    def prepare_summaries(self):
        with st.spinner("Preparing summaries..."):
            title = self.references["Title"]
            #load indexes from storage
            storage_context = StorageContext.from_defaults(persist_dir=self.paths["INDEX_STORAGE"])
            tree_index = load_index_from_storage(storage_context, index_id="tree")
            query_engine = tree_index.as_query_engine(llm = self.llm)
            
            topic_dict = self._extract_topic()
            
            materials = []
            summarizations = []
            for topic, subtopics in topic_dict.items():
                # Get RAG 
                topic_explanation_prompt = Template(human_topic_explanation_template).render(topic=topic)
                topic_explain = str(query_engine.query(topic_explanation_prompt))
                
                overview = Summarizer(title, topic, subtopic = f"Overview - {topic}", summarization= topic_explain)
                summarizations.append(overview)
                
                topic_explain = f"# {topic} \n\n {topic_explain}"
                print(topic_explain)  # Print the topic
                materials.append(topic_explain)
                
                for subtopic in subtopics:
                    print(f"Generate content_table for {topic} - {subtopic}")
                    # Get RAG 
                    sub_topic_explanation_prompt = Template(human_sub_topic_explanation_template).render(topic=topic, sub_topic=subtopic)
                    sub_topic_explain = str(query_engine.query(sub_topic_explanation_prompt))

                    summarization = Summarizer(title, topic, subtopic, sub_topic_explain)
                    summarizations.append(summarization)
                    
                    sub_topic_explain = f"# {subtopic} \n\n {sub_topic_explain}"
                    print(sub_topic_explain)  # Print the sub topic                    
                    materials.append(sub_topic_explain)
            
            complete_summarization = "\n".join(materials)
            
            # Tentukan nama file Markdown
            file_name = "summarization.md"
            summarization_dir = self.paths["SUMMARIZATION_RESULT"]
            if not os.path.exists(summarization_dir):
                os.makedirs(summarization_dir)

            # Construct the file path
            file_path = os.path.join(summarization_dir, file_name)
            # Tulis hasil summarization ke dalam file Markdown
            with open(file_path, "w",  encoding="utf-8") as file:
                file.write("# Summary\n\n")  # Header Markdown
                file.write(complete_summarization)
            
            summarization_deck = SummarizationDeck(self.references["Title"], summarizations)
            summarization_deck.save_to_file(self.paths["SUMMARIZATION_FILE"])
                
            st.info("Summarization generated!")                