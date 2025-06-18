from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.dag import run_pipeline
# from app.pipeline import run_pipeline
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Customer 360° Recommender API",
    description="""
    📊 This API provides detailed cross-sell and upsell recommendations
    using a LangGraph-powered modular agent system.

    🧠 Agents include:
    - Customer context extraction
    - Purchase pattern analysis
    - Product affinity detection
    - Opportunity scoring
    - Research report generation

    📈 Use `/recommendation` to fetch a complete research report for any customer.
    """,
    version="1.0.0",
    contact={
        "name": "Yash Dewangan",
        "url": "https://github.com/yashdew3/LangGraph-Customer360-Recommender",
        "email": "yashdew06@gmail.com",
    }
)

# Allow all CORS (optional: secure if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/recommendation", summary="Get customer recommendation report", tags=["Recommendation"])
def get_recommendation(
    customer_id: str = Query(..., description="Customer ID like 'C001'")
):
    """
    🎯 Generate a cross-sell/upsell research report for the given customer.

    **Returns:**
    - `report_text`: Full natural-language research report
    - `executive_summary`: Short summary of key findings
    - `recommendations`: Structured list of product recommendations
    """
    result = run_pipeline(customer_id)

    if "error" in result:
        return JSONResponse(status_code=404, content={"error": result["error"]})

    return result
