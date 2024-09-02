import streamlit as st 
from datetime import datetime
from src.global_settings import get_paths 
from llama_index.core.llms import ChatMessage


class ChatInterface:
    def __init__(self, chat_bot, chat_store_manager):
        self.chat_bot = chat_bot
        self.chat_store_manager = chat_store_manager
        
    def display_messages(self, container, sources):
        last_tool_message = None  # Variable untuk menyimpan pesan 'tool' terakhir

        with container:
            for message in self.chat_store_manager.get_messages():
                # Skip rendering if the content is None
                if message.content is None:
                    continue

                with st.chat_message(message.role):
                    st.markdown(f"**{message.role.capitalize()}** : {message.content}")

            # Render sources hanya jika ada pesan 'tool' terakhir
            if sources != "" :
                with st.chat_message("reference"):
                        st.markdown(f"**Sources** : \n {sources}")


    def handle_user_input(self):
        prompt = st.chat_input("Type your question here:")
        if prompt:
            response = self.chat_bot.get_response(prompt)
            sources = self.chat_bot.get_sources(prompt)
            self.chat_store_manager.persist_chat_store()
            return sources

    def delete_chat_history(self):
        self.chat_store_manager.clear_chat_store()
        st.write("Chat history has been cleared.")   