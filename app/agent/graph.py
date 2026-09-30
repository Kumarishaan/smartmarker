from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.state import AgentState
from app.agent.agent import llm


def build_agent_graph(tools, checkpointer):

    llm_with_tools = llm.bind_tools(tools)

    async def call_llm(state: AgentState):
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}



    builder = StateGraph(AgentState)

    builder.add_node("llm", call_llm)
    builder.add_node("tools", ToolNode(tools))
    

    builder.add_edge(START, "llm")
    builder.add_conditional_edges("llm", tools_condition)
    builder.add_edge("tools", "llm")

    return builder.compile(checkpointer=checkpointer)
