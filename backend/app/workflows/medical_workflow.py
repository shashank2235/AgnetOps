from typing import TypedDict

from langgraph.graph import END, StateGraph


class MedicalWorkflowState(TypedDict):
    query: str
    contexts: list[str]
    graph_entities: list[dict]
    guardrail_action: str
    answer: str


def build_medical_workflow():
    graph = StateGraph(MedicalWorkflowState)

    def retrieve(state: MedicalWorkflowState):
        state["contexts"] = ["chunk-001", "chunk-002"]
        return state

    def graph_lookup(state: MedicalWorkflowState):
        state["graph_entities"] = [{"name": "Medical Policy 101"}]
        return state

    def finalize(state: MedicalWorkflowState):
        state["answer"] = f"Policy-based answer for: {state['query']}"
        return state

    graph.add_node("retrieve", retrieve)
    graph.add_node("graph_lookup", graph_lookup)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "graph_lookup")
    graph.add_edge("graph_lookup", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile()
