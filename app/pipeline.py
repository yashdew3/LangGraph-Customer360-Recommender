from app.agents.customer_context import get_customer_context
from app.db import fetch_customer_activities
from app.agents.purchase_analysis import purchase_pattern_analysis
from app.agents.product_affinity import product_affinity_analysis
from app.agents.opportunity_scoring import score_opportunities
from app.agents.report_generator import generate_report

def run_pipeline(customer_id: str) -> dict:
    try:
        # Step 1: Customer Context
        profile = get_customer_context(customer_id)
        if "error" in profile:
            return {"error": f"Customer ID {customer_id} not found."}

        # Step 2: Activity Log
        activities = fetch_customer_activities(customer_id)

        # Step 3: Purchase Pattern Analysis
        pattern = purchase_pattern_analysis(profile, activities)

        # Step 4: Product Affinity
        affinity = product_affinity_analysis(profile["current_products"].split(", "))

        # Step 5: Opportunity Scoring
        scored = score_opportunities(profile, pattern, affinity, activities)

        # Step 6: Generate Report
        report = generate_report(profile, scored["scored_opportunities"])

        return {
            "customer_id": customer_id,
            "report_text": report["report_text"],
            "executive_summary": report["executive_summary"],
            "recommendations": report["structured_recommendations"]
        }

    except Exception as e:
        return {"error": str(e)}
