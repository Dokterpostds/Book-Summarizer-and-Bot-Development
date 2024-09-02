from langgraph.graph import END, StateGraph
from src.graph_code.nodes import Nodes
from src.graph_code.state import AgentCreator
from langgraph.graph import END, StateGraph
from IPython.display import Image
import os
from dotenv import load_dotenv
        

def design_graph(api_key, model, temperature, path_pdf):
    
    if api_key:
        os.environ['OPENAI_API_KEY']=api_key
    else:
        load_dotenv()
    graph_process = Nodes(model, temperature, path_pdf)
    workflow = StateGraph(AgentCreator)
    
    # Define the nodes
    workflow.add_node("topic_given", graph_process.get_the_topic)
    workflow.add_node("creator",graph_process.evaluator)
    workflow.add_node("summarizer", graph_process.repairer)  

    # Build graph
    workflow.set_entry_point("topic_given")
    workflow.add_edge("upload_script", "evaluator")
    workflow.add_edge("evaluator", "repairer")
    workflow.add_edge("repairer", "extractor")
    workflow.add_edge("extractor", "summarizer")
    workflow.add_edge("summarizer", "reviewer")
    workflow.add_conditional_edges(
        'reviewer',
        graph_process.decide_to_improver,
        {
            "need_to_review": "improver",
            "no_review": END    
        }
    )
    workflow.add_edge("improver", "reviewer")
    # Compile
    app = workflow.compile()
    # flowchart =Image(app.get_graph().draw_png())
    return app