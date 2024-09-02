from crewai_tools import PDFSearchTool


def search_pdf(path_file): # Loopimng  di embedding berulang ulang?? 
    rag_tool = PDFSearchTool(pdf='doc.pdf',
        config=dict(
            llm=dict(
                provider="groq", # or google, openai, anthropic, llama2, ...
                config=dict(
                    model="llama3-8b-8192",
                    # temperature=0.5,
                    # top_p=1,
                    # stream=true,
                ),
            ),
            embedder=dict(
                provider="huggingface", # or openai, ollama, ...
                config=dict(
                    model="BAAI/bge-small-en-v1.5",
                    #task_type="retrieval_document",
                    # title="Embeddings",
                ),
            ),
        )
    )

# Create tools from serpi AI



