from interface.onboarding_ui import user_onboarding, upload_file
from src.session_function import SessionManager
from src.logging import ActionLogger
# from interface.quiz_ui import show_quiz
from interface.summarizer_ui import show_training_UI
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()


def main():
    st.set_page_config(layout="wide")
    st.sidebar.title('Book Summarizer')
    st.sidebar.markdown('### Book Summarizer and Study Chatbot')

    # Load API Key from environment or user input
    # if 'OPENAI_API_KEY' not in st.session_state or not st.session_state['OPENAI_API_KEY']:
    #     api_key = st.text_input("Enter your OpenAI API Key (or leave blank if running locally): ")
    #     if api_key:
    #         st.session_state['OPENAI_API_KEY'] = api_key
    #         os.environ['OPENAI_API_KEY'] = api_key
    #     else:
    #         api_key  = os.getenv('OPENAI_API_KEY')
    #         os.environ['OPENAI_API_KEY'] = api_key


    api_key = st.text_input("Enter your OpenAI API Key (or leave blank if running locally): ",
                            type="password",
                            value=os.environ.get("OPENAI_API_KEY", None))
    # api_key = os.getenv('OPENAI_API_KEY')
    st.session_state['OPENAI_API_KEY'] = api_key
    os.environ['OPENAI_API_KEY'] = api_key            

    references = user_onboarding()
    if references:
        st.write("Book Details:", references)
        logger = ActionLogger(references["Theme"], references["Title"])
        sessionmanager = SessionManager(references["Theme"], references["Title"])

        # Load the session only once
        session_data = sessionmanager.load_session(st.session_state)
        
        # # Check if the user is returning and has opted to take a quiz
        # if 'show_quiz' in session_data and session_data['show_quiz']:
        #     show_quiz(st.session_state['study_subject'])  # Show the quiz screen immediately

        if 'resume_session' in st.session_state and st.session_state['resume_session']:
            # If resuming, clear previous content and show the training UI
            show_training_UI(st.session_state['user_name'], references)
            # st.session_state['show_quiz'] = False  # Ensure quiz is not shown
            # show_training_UI(st.session_state['user_name'], st.session_state['study_subject'])
        elif not session_data:
            upload_file(references)  # Show the onboarding screen for new users
        else:
            # For returning users, display options to resume or start a new session
            st.write(f"Welcome back {st.session_state['user_name']}!")
            col1, col2, = st.columns(2)
            if col1.button(f"Resume your study of {st.session_state['theme']}"):
                # Mark the session to be resumed and rerun to clear previous content
                st.session_state['resume_session'] = True
                st.rerun()
            if col2.button("Add new book"):
                upload_file(references)     
            if col2.button('Start a new session'):
                sessionmanager.delete_session(st.session_state)
                logger.reset_log()
                # Clear session state and rerun for a fresh start
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main()