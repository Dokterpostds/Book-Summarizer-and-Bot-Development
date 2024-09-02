import asyncio
import logging
from langchain.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain.runnables import RunnableSequence, RunnableMap, RunnableLambda
from langchain.output_parsers import StringOutputParser
from langchain.documents import Document
from langchain.core.language_models import BaseChatModel
from langchain.embeddings import Embeddings
from langchain.core.messages import BaseMessage
from langchain.core.tracers import StreamEvent
from langchain.core.tracers.log_stream import EventEmitter
from search_searxng import search_searxng
from utils import format_chat_history_as_string, compute_similarity

# Setting up logging
logger = logging.getLogger(__name__)

basic_academic_search_retriever_prompt = """
You will be given a conversation below and a follow-up question. You need to rephrase the follow-up question if needed so it is a standalone question that can be used by the LLM to search the web for information.
If it is a writing task or a simple hi, hello rather than a question, you need to return `not_needed` as the response.

Example:
1. Follow-up question: How does stable diffusion work?
Rephrased: Stable diffusion working

2. Follow-up question: What is linear algebra?
Rephrased: Linear algebra

3. Follow-up question: What is the third law of thermodynamics?
Rephrased: Third law of thermodynamics

Conversation:
{chat_history}

Follow-up question: {query}
Rephrased question:
"""

basic_academic_search_response_prompt = """
You are Perplexica, an AI model who is expert at searching the web and answering user's queries. You are set on focus mode 'Academic', this means you will be searching for academic papers and articles on the web.

Generate a response that is informative and relevant to the user's query based on provided context (the context consists of search results containing a brief description of the content of that page).
You must use this context to answer the user's query in the best way possible. Use an unbiased and journalistic tone in your response. Do not repeat the text.
You must not tell the user to open any link or visit any website to get the answer. You must provide the answer in the response itself. If the user asks for links you can provide them.
Your responses should be medium to long in length, informative, and relevant to the user's query. You can use markdown to format your response. You should use bullet points to list the information. Make sure the answer is not short and is informative.
You have to cite the answer using [number] notation. You must cite the sentences with their relevant context number. You must cite each and every part of the answer so the user can know where the information is coming from.
Place these citations at the end of that particular sentence. You can cite the same sentence multiple times if it is relevant to the user's query like [number1][number2].
However, you do not need to cite it using the same number. You can use different numbers to cite the same sentence multiple times. The number refers to the number of the search result (passed in the context) used to generate that part of the answer.

Anything inside the following `context` HTML block provided below is for your knowledge returned by the search engine and is not shared by the user. You have to answer the question on the basis of it and cite the relevant information from it but you do not have to 
talk about the context in your response. 

<context>
{context}
</context>

If you think there's nothing relevant in the search results, you can say that 'Hmm, sorry I could not find any relevant information on this topic. Would you like me to search again or ask something else?'.
Anything between the `context` is retrieved from a search engine and is not a part of the conversation with the user. Today's date is {date}
"""

str_parser = StringOutputParser()

async def handle_stream(stream: asyncio.StreamReader, emitter: EventEmitter):
    async for event in stream:
        if event.event == 'on_chain_end' and event.name == 'FinalSourceRetriever':
            emitter.emit('data', {'type': 'sources', 'data': event.data['output']})
        elif event.event == 'on_chain_stream' and event.name == 'FinalResponseGenerator':
            emitter.emit('data', {'type': 'response', 'data': event.data['chunk']})
        elif event.event == 'on_chain_end' and event.name == 'FinalResponseGenerator':
            emitter.emit('end')

def create_basic_academic_search_retriever_chain(llm: BaseChatModel):
    return RunnableSequence([
        PromptTemplate.from_template(basic_academic_search_retriever_prompt),
        llm,
        str_parser,
        RunnableLambda(lambda input: {'query': '', 'docs': []} if input == 'not_needed' else asyncio.run(search_and_process(input)))
    ])

async def search_and_process(input: str):
    res = await search_searxng(input, {'language': 'en', 'engines': ['arxiv', 'google scholar', 'internetarchivescholar', 'pubmed']})
    documents = [
        Document(page_content=result['content'], metadata={'title': result['title'], 'url': result['url'], 'img_src': result.get('img_src')})
        for result in res.results
    ]
    return {'query': input, 'docs': documents}

def create_basic_academic_search_answering_chain(llm: BaseChatModel, embeddings: Embeddings):
    basic_academic_search_retriever_chain = create_basic_academic_search_retriever_chain(llm)

    async def process_docs(docs):
        return "\n".join([f"{i + 1}. {doc.page_content}" for i, doc in enumerate(docs)])

    async def rerank_docs(query, docs):
        if not docs:
            return docs

        docs_with_content = [doc for doc in docs if doc.page_content]
        doc_embeddings, query_embedding = await asyncio.gather(
            embeddings.embed_documents([doc.page_content for doc in docs_with_content]),
            embeddings.embed_query(query)
        )

        similarity = [
            {'index': i, 'similarity': compute_similarity(query_embedding, doc_embedding)}
            for i, doc_embedding in enumerate(doc_embeddings)
        ]

        sorted_docs = sorted(similarity, key=lambda x: x['similarity'], reverse=True)[:15]
        return [docs_with_content[sim['index']] for sim in sorted_docs]

    return RunnableSequence([
        RunnableMap({
            'query': lambda input: input['query'],
            'chat_history': lambda input: input['chat_history'],
            'context': RunnableSequence([
                lambda input: {
                    'query': input['query'],
                    'chat_history': format_chat_history_as_string(input['chat_history']),
                },
                basic_academic_search_retriever_chain
                .pipe(rerank_docs)
                .with_config(run_name='FinalSourceRetriever')
                .pipe(process_docs),
            ]),
        }),
        ChatPromptTemplate.from_messages([
            ('system', basic_academic_search_response_prompt),
            MessagesPlaceholder('chat_history'),
            ('user', '{query}')
        ]),
        llm,
        str_parser,
    ]).with_config(run_name='FinalResponseGenerator')

async def basic_academic_search(query: str, history: list[BaseMessage], llm: BaseChatModel, embeddings: Embeddings):
    emitter = EventEmitter()

    try:
        basic_academic_search_answering_chain = create_basic_academic_search_answering_chain(llm, embeddings)
        stream = basic_academic_search_answering_chain.stream_events(
            {'chat_history': history, 'query': query}, {'version': 'v1'}
        )
        await handle_stream(stream, emitter)
    except Exception as err:
        emitter.emit('error', {'data': 'An error has occurred please try again later'})
        logger.error(f"Error in academic search: {err}")

    return emitter

def handle_academic_search(message: str, history: list[BaseMessage], llm: BaseChatModel, embeddings: Embeddings):
    return asyncio.run(basic_academic_search(message, history, llm, embeddings))
