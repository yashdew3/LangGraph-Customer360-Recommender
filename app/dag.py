from langgraph.graph import StateGraph
from langgraph.graph.message import MessageGraph  # optional, remove if not used
from typing import TypedDict, Dict, List

# Import agents
from app.agents.customer_context import get_customer_context
from app.agents.purchase_analysis import purchase_pattern_analysis
from app.agents.product_affinity import product_affinity_analysis
from app.agents.opportunity_scoring import score_opportunities
from app.agents.report_generator import generate_report
from app.db import fetch_customer_activities

# LangGraph state structure
class AgentState(TypedDict):
    customer_id: str
    customer_profile: dict
    activity_log: list
    purchase_analysis: dict
    product_affinity: dict
    opportunity_score: dict
    report: dict

# Define LangGraph nodes (agents)
def customer_context_agent(state: AgentState) -> AgentState:
    profile = get_customer_context(state["customer_id"])
    return {**state, "customer_profile": profile}

def activity_log_agent(state: AgentState) -> AgentState:
    logs = fetch_customer_activities(state["customer_id"])
    return {**state, "activity_log": logs}

def purchase_analysis_agent(state: AgentState) -> AgentState:
    result = purchase_pattern_analysis(state["customer_profile"], state["activity_log"])
    return {**state, "purchase_analysis": result}

def product_affinity_agent(state: AgentState) -> AgentState:
    products = state["customer_profile"]["current_products"].split(", ")
    result = product_affinity_analysis(products)
    return {**state, "product_affinity": result}

def scoring_agent(state: AgentState) -> AgentState:
    result = score_opportunities(
        state["customer_profile"],
        state["purchase_analysis"],
        state["product_affinity"],
        state["activity_log"]
    )
    return {**state, "opportunity_score": result}

def report_agent(state: AgentState) -> AgentState:
    result = generate_report(
        state["customer_profile"],
        state["opportunity_score"]["scored_opportunities"]
    )
    return {**state, "report": result}

# Build DAG
builder = StateGraph(AgentState)

builder.add_node("CustomerContext", customer_context_agent)
builder.add_node("ActivityLog", activity_log_agent)
builder.add_node("PurchaseAnalysis", purchase_analysis_agent)
builder.add_node("ProductAffinity", product_affinity_agent)
builder.add_node("OpportunityScoring", scoring_agent)
builder.add_node("ReportGenerator", report_agent)

# Define flow
builder.set_entry_point("CustomerContext")
builder.add_edge("CustomerContext", "ActivityLog")
builder.add_edge("ActivityLog", "PurchaseAnalysis")
builder.add_edge("PurchaseAnalysis", "ProductAffinity")
builder.add_edge("ProductAffinity", "OpportunityScoring")
builder.add_edge("OpportunityScoring", "ReportGenerator")

# Compile
graph = builder.compile()

# Entry function
def run_pipeline(customer_id: str) -> Dict:
    initial_state = {"customer_id": customer_id}
    final_state = graph.invoke(initial_state)
    return final_state["report"]
