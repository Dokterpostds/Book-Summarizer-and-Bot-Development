import json
from turtle import width
import streamlit as st
from src.summarizer.summarization import SummarizationDeck
from openai import OpenAI
from pathlib import Path
from src.chatbot.bot_conversation import ChatStoreManager, ChatBot
from interface.bot_ui import ChatInterface
from src.global_settings import get_paths

def show_training_UI(user_name, references):
    theme = references["Theme"]
    title = references["Title"]

    chat_store_manager = ChatStoreManager(theme, title)
    chat_bot = ChatBot(user_name, chat_store_manager, references)
    chat_interface = ChatInterface(chat_bot, chat_store_manager)
    
    theme = references["Theme"]
    title = references["Title"]
    # Load the slide deck
    paths = get_paths(theme, title)
    summarization_path = paths["SUMMARIZATION_FILE"]
    
    summarization_deck = SummarizationDeck.load_from_file(summarization_path)
    
    
    # Display title and slide navigation controls
    st.sidebar.markdown("## " + summarization_deck.title)
    current_slide_index = st.sidebar.number_input("Summmarizer Number", min_value=1, max_value=len(summarization_deck.summarizations), value=1, step=1)
    current_slide = summarization_deck.summarizations[current_slide_index-1]
    if st.sidebar.button("Toggle narration"):
            st.session_state.show_narration = not st.session_state.get('show_narration', False)

    # Displaying slides and narration in the main area
    col1, col2 = st.columns([0.6,0.4],gap="medium")
    with col1:
        st.markdown(current_slide.render(display_narration=st.session_state.get('show_narration', False)),           
                    unsafe_allow_html=True)

    # Chatbot integration in the sidebar
    with col2:
        
        st.header("💬 Study Chatbot")
        st.success(f"Hello {user_name}. I'm here to answer questions about {theme}")
        #with st.spinner("Preparing the chatbot..."):
        chat_store = chat_store_manager.load_chat_store()
        container = st.container(height=600)
        sources  = chat_interface.handle_user_input()
        chat_interface.display_messages(container, sources)
        
        if st.button("Clear Chat History"):
            chat_interface.delete_chat_history()
            st.rerun()
            
        
