from openai import OpenAI
import os
import base64
import fitz
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.callbacks import get_openai_callback
from src.prompt import get_the_topics_template, refined_get_topic_template


class Extractor:
    def __init__(self, client):
        self.client = client
        self.token_used = 0
        self.prompt_token = 0
        self.completion_token = 0
        
    def topic_extractor(self, topics_image):
        responses = []

        try: 
            # Open the PDF file
            content_table = fitz.open(stream=topics_image.read(), filetype="pdf") 
            # content_table = fitz.open(topics_image)
        except Exception as e:
            print(f"Error opening PDF file: {e}")
            return responses, 0  # Return 0 token usage if there's an error

        # Initialize a list to collect base64 encoded images
        pix_encoded_combined = []

        # Iterate over each page to extract images
        for page_number in range(len(content_table)):
            try:
                page = content_table.load_page(page_number)
                pix_encoded = self._extract_image_as_base64(page)
                pix_encoded_combined.append(pix_encoded)
            except Exception as e:
                print(f"Error processing page {page_number}: {e}")
                continue  # Skip to the next page if there's an error

        if not pix_encoded_combined:
            print("No images extracted from the PDF.")
            return responses, 0  # Return 0 token usage if no images were extracted

        # Initialize OpenAI client
        client_openai = OpenAI()

        # Get response from OpenAI
        try:
            response, token_usage = self._response_topic_images(client_openai, pix_encoded_combined)
            self._update_tokens(token_usage)
        except Exception as e:
            print(f"Error getting response from OpenAI: {e}")
            return responses, 0  # Return 0 token usage if there's an error

        # Generate extractor agent
        try:
            extractor_agent, extractor_info = self._generate_extractor_agent(response)
            self._update_tokens(extractor_info)
        except Exception as e:
            print(f"Error generating extractor agent: {e}")
            return responses, 0  # Return 0 token usage if there's an error

        responses.append(extractor_agent)

        # Join responses and get token usage
        responses_text = '\n'.join(responses)
        token_usage = self._get_token_usage()

        return responses_text, token_usage
    
    def _extract_image_as_base64(self, page):
        pix = page.get_pixmap()
        pix_bytes = pix.tobytes()
        return base64.b64encode(pix_bytes).decode('utf-8')    

    def _response_topic_images(self, client_open_ai, images):
        # Prepare the list of image messages
        image_messages = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}",
                }
            }
            for image in images
        ]
        
        # Add a text message at the beginning
        messages = [
            {"role": "system", "content": "Kamu adalah sistem yang berfungsi untuk ekstraksi gambar"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": get_the_topics_template},
                    *image_messages
                ]
            }
        ]
        
        # Create the completion request
        completion = client_open_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
        )

        # Extract the response and token usage
        response = completion.choices[0].message.content
        token_usage = completion.usage

        return response, token_usage
    
    def _generate_extractor_agent(self, response):
        extractor_gen_prompt = ChatPromptTemplate.from_messages([
            ("system", "You should follow the instructions given"),
            ("human", refined_get_topic_template)
        ])

        extractor_chain = extractor_gen_prompt | self.client | StrOutputParser()

        with get_openai_callback() as extractor_info:
            extractor_agent = extractor_chain.invoke({'topics': response})

        return extractor_agent, extractor_info 
        
    def _update_tokens(self, token_info):
        self.token_used += token_info.total_tokens
        self.prompt_token += token_info.prompt_tokens
        self.completion_token += token_info.completion_tokens

    def _get_token_usage(self):
        return {
            "total_tokens": self.token_used,
            "prompt_tokens": self.prompt_token,
            "completion_tokens": self.completion_token
        }      