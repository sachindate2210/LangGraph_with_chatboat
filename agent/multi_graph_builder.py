from langgraph.graph import StateGraph, END

from agent.multi_graph_state import MultiAgentState
from agent.multi_graph_nodes import (
    memory_retrieval_node,
    manager_node,
    router_node,
    chat_node,
    research_agent_node,
    calculator_agent_node,
    weather_agent_node,
    database_agent_node,
    file_agent_node,
    email_agent_node,
    final_response_node
)


def build_multi_agent_graph():

    graph = StateGraph(MultiAgentState)

    # -----------------------------------------------
    # NODES
    # -----------------------------------------------

    graph.add_node("memory_retrieval",  memory_retrieval_node)
    graph.add_node("manager",           manager_node)
    graph.add_node("router",            router_node)
    graph.add_node("chat_agent",        chat_node)
    graph.add_node("research_agent",    research_agent_node)
    graph.add_node("calculator_agent",  calculator_agent_node)
    graph.add_node("weather_agent",     weather_agent_node)
    graph.add_node("database_agent",    database_agent_node)
    graph.add_node("file_agent",        file_agent_node)
    graph.add_node("email_agent",       email_agent_node)
    graph.add_node("final_response",    final_response_node)

    # -----------------------------------------------
    # FLOW: memory → manager → router
    # -----------------------------------------------

    graph.set_entry_point("memory_retrieval")
    graph.add_edge("memory_retrieval", "manager")
    graph.add_edge("manager",          "router")

    # -----------------------------------------------
    # ROUTER → Agent (based on current_task)
    # -----------------------------------------------

    graph.add_conditional_edges(
        "router",
        lambda state: state["current_task"],
        {
            "chat":       "chat_agent",
            "research":   "research_agent",
            "calculator": "calculator_agent",
            "weather":    "weather_agent",
            "database":   "database_agent",
            "file":       "file_agent",
            "email":      "email_agent",
            "done":       "final_response",
        }
    )

    # -----------------------------------------------
    # Agent complete → Router wapas (queue se next task)
    # -----------------------------------------------

    graph.add_edge("chat_agent",       "router")
    graph.add_edge("research_agent",   "router")
    graph.add_edge("calculator_agent", "router")
    graph.add_edge("weather_agent",    "router")
    graph.add_edge("database_agent",   "router")
    graph.add_edge("file_agent",       "router")
    graph.add_edge("email_agent",      "router")

    # -----------------------------------------------
    # END
    # -----------------------------------------------

    graph.add_edge("final_response", END)

    return graph.compile()


multi_agent_graph = build_multi_agent_graph()
