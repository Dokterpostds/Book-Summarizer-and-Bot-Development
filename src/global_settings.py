def get_paths(theme: str, title: str) -> dict:
    """
    Generates and returns paths for various files based on the provided theme.

    Parameters:
    - theme (str): The theme for which to generate paths.

    Returns:
    - dict: A dictionary containing paths for log, session, cache, conversation, quiz, slides, storage, and index storage files.
    """
    paths = {
        "LOG_FILE": f"database/session_data/{theme}/user_actions.log",
        "SESSION_FILE": f"database/session_data/{theme}/user_session_state.yaml",
        "CACHE_FILE": f"database/cache/{theme}/{title}/pipeline_cache.json",
        "CONVERSATION_FILE": f"database/history_chat/{theme}/chat_history.json",
        "QUIZ_FILE": f"database/cache/{theme}/quiz.csv",
        "SUMMARIZATION_FILE": f"database/cache/{theme}/{title}/summarization.json",
        "STORAGE_PATH": f"book_collection/ingestion_storage/{theme}/{title}/",
        "INDEX_STORAGE": f"database/index_storage/{theme}/{title}/",
        "MERGE_PATH" : f"database/index_storage/{theme}/",
        "BOOK_TITLES" : f"database/books_titles/{theme}/",
        "SUMMARIZATION_RESULT": f"output/summarization/{theme}/{title}/"  
    }
    return paths


QUIZ_SIZE = 5
ITEMS_ON_SLIDE = 4
