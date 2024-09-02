import os
import json
import streamlit as st
from io import BytesIO
from src.session_function import SessionManager
from src.global_settings import get_paths
from src.ingestion_data.document_uploader import Uploader
from src.summarizer.summarizer_builder import SummarizeGenerator
from src.ingestion_data.index_builder import IndexManager

def user_onboarding():
    user_name = st.text_input('What is your name?')
    if not user_name: return

    st.session_state['user_name'] = user_name
    st.write(f"Hello {user_name}. It's nice meeting you!")

    theme = st.text_input('What is the theme of the book?')
    if not theme: return

    st.session_state['theme'] = theme
    st.write(f"Okay {user_name}, let's focus on {theme}.")

    st.header("Input the details of the book")

    references = {
        "Theme": theme,
        "Title": st.text_input("Title: "),
        "Author": st.text_input("Author: "),
        "Publisher": st.text_input("Publisher: "),
        "Year": st.text_input("Year: ")
    }

    st.session_state.update(references)
    return references

def upload_file(references):
    required_fields = ["Title", "Theme", "Author", "Publisher", "Year"]
    missing_fields = [field for field in required_fields if not references.get(field)]

    if missing_fields:
        st.error(f"Please complete the following details before uploading: {', '.join(missing_fields)}")
    else:
        paths = get_paths(references["Theme"], references["Title"])
        uploader = Uploader(references)
        index = IndexManager(references["Theme"], references["Title"])

        st.write("Please upload the book...")
        uploaded_file = st.file_uploader("Choose files", accept_multiple_files=False)
        content_table = st.file_uploader("Content Table", accept_multiple_files=False)
        
        finish_upload = st.button('FINISH UPLOAD')
        
        if finish_upload and uploaded_file and content_table:
            _handle_file_upload(uploaded_file, paths["STORAGE_PATH"])  
            st.info('Uploading files...')
            st.session_state['uploaded_files'] = uploaded_file.name
            st.session_state['finish_upload'] = True
                      
        if 'finish_upload' in st.session_state:
            # summarize_book = st.button('SUMMARIZE BOOK')
            # if summarize_book:
            # try: 
            summarizer = SummarizeGenerator(content_table, references)  # Initialize with content_table and references
            process_post_upload_content(index, uploader, summarizer, references)
            # except Exception as e:
            # st.error(f"An error occurred: {str(e)}")
               
def _handle_file_upload(uploaded_file, storage_dir):
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
        st.write(f"Directory {storage_dir} created.")
    file_path = os.path.join(storage_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.write(f"You have uploaded {uploaded_file.name}")

def process_post_upload_content(index, uploader, summarizer, references):
    st.write('Please select your current knowledge level on the topic')
    difficulty_level = st.radio(
        'Current knowledge:',
        ['Beginner', 'Intermediate', 'Advanced', 'Take a quiz to assess'],
    )
    st.session_state['difficulty_level'] = difficulty_level

    index_button = st.button('Build Indexing')
    if index_button:
        st.info('Ingesting study materials first...')
        nodes_with_metadata = uploader.process_documents()
        st.info('Materials loaded. Preparing indexes...')
        keyword_index, vector_index = index.build_indexes(nodes_with_metadata)
        st.info('Indexing complete.')
        
    summarize_button = st.button('Summarize')
    if summarize_button:
        st.info('Generating summarization...')
        summarizer.prepare_summaries() # Uncomment when slides generation is implemented
        print("Finished summarizing")
        _handle_session_management(references)

def _handle_session_management(references):
    sessionmanager = SessionManager(references["Theme"], references["Title"])
    titles_dir = get_paths(references["Theme"], references["Title"])["BOOK_TITLES"]
    json_file_path = os.path.join(titles_dir, "list_title.json")

    if not os.path.exists(titles_dir):
        os.makedirs(titles_dir)

    list_title = []
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            list_title = json.load(file)

    list_title.append(references)
    with open(json_file_path, "w") as file:
        json.dump(list_title, file, indent=4)

    sessionmanager.save_session(st.session_state)
    st.write(f"Updated list_title saved to {json_file_path}.")