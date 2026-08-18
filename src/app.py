from __future__ import annotations

from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    message: str


def bootstrap_node(state: AgentState) -> AgentState:
    # Placeholder node to verify LangGraph wiring end-to-end.
    return {"message": f"LangGraph initialized. Input: {state['message']}"}


def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("bootstrap", bootstrap_node)
    workflow.add_edge(START, "bootstrap")
    workflow.add_edge("bootstrap", END)
    return workflow.compile()


def main() -> None:
    load_dotenv()
    graph = build_graph()
    result = graph.invoke({"message": "Hello"})
    print(result["message"])


if __name__ == "__main__":
    main()
