from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain_core.output_parsers import StrOutputParser
from langchain_google_vertexai import ChatVertexAI
from src.extractor import Extractor
from src.prompt import (
    system_topic_explanation_template,
    human_topic_explanation_template,
    system_sub_topic_explanation_template,
    human_sub_topic_explanation_template,
    system_summarize_template,
    human_summarize_template
)
from src.preprocessing.parsing import parse_topics_to_dict


class Invoke():
    def __init__(self, model, temperature, document, topic):
        # self.client=ChatOpenAI(model="gpt-4o", temperature=0.2)
        if model in ["gpt-4o", "gpt-3.5-turbo", "gpt-4o-mini"]:
            self.client = ChatOpenAI(model=model, temperature=temperature)    
        else:
            self.client = ChatVertexAI(model="gemini-pro", temperature=temperature)
        self.topic = topic
        self.extractor = Extractor(self.client)

    def get_topic(self, topic_images):
        try: 
            topic_extractor, token_usage = self.extractor.topic_extractor(topic_images)
            topic_dict = dict(parse_topics_to_dict(topic_extractor))

            return topic_extractor, topic_dict
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return e
    
    def creator_invoke(self, topic_dict):
        try:
            # Loop through the dictionary
            materials = []

            context = ["RAG PDF"]
            # Upload PDF file
            # Menggunakan rerangker

            for topic, sub_topics in topic_dict.items():
                topic_gen_prompt = self._generate_prompt_template(
                    system_topic_explanation_template,
                    human_topic_explanation_template
                )
                # Chain
                topic_chain = topic_gen_prompt | self.client | StrOutputParser()
                with get_openai_callback() as topic_info:
                    topic_agent = topic_chain.invoke({'topic':topic, 'context':context})

                print(topic_agent)  # Print the topic
                materials.append(topic_agent)
                
                sub_topics_material = []

                for sub_topic in sub_topics:
                    # Generate the sub-topic explanation prompt
                    sub_topic_gen_prompt = self._generate_prompt_template(
                        system_sub_topic_explanation_template,
                        human_sub_topic_explanation_template
                    )
                    sub_topic_chain = sub_topic_gen_prompt | self.client | StrOutputParser()
                    
                    # Invoke the chain for the sub-topuc
                    with get_openai_callback() as sub_topic_info:
                        sub_topic_agent = sub_topic_chain.invoke({
                            'topic':topic,
                            'subtopic': sub_topic,
                            'context':context
                        })
                    print(sub_topic_agent)  # Print the sub-topic
                    sub_topic.append(sub_topic_agent)

                sub_topics_material_str = "\n".join(sub_topics_material)

                material_each_chapter = f"{topic_agent}\n\n{sub_topics_material_str}"
                materials.append(material_each_chapter)

                # Summarize the material for each chapter
                summarizer = self.summarizer_invoke(material_each_chapter)
            
            # Join all materials into a single string
            materials = '\n'.join(materials)

            return materials, summarizer

        except Exception as e:
            print(f"An error occurred: {e}")
            return e
    
    def summarizer_invoke(self, material_each_chapter):
        try: 
            summarizer_prompt = self._generate_prompt_template(
                system_summarize_template,
                human_summarize_template
            )

            summarizer_chain = summarizer_prompt | self.client | StrOutputParser()
            
            with get_openai_callback() as summarizer_info:
                summarizer_agent = summarizer_chain.invoke({'text': material_each_chapter})

            return summarizer_agent
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return e

    def _generate_prompt_template(self, system_template, human_template):
        return ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("human", human_template),
            ]
        )
