from typing import Dict, List
from transformers import pipeline


summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_report(customer_profile: Dict, scored_opportunities: List[Dict]) -> Dict:
    company = customer_profile.get("customer_name", "This client")
    industry = customer_profile.get("industry", "General Industry")
    revenue = customer_profile.get("annual_revenue", 0)
    location = customer_profile.get("location", "")
    current_products = customer_profile.get("current_products", "")
    usage = customer_profile.get("product_usage_percent", 0)

    intro = (
        f"Research Report: Cross-Sell and Upsell Opportunities for {company}\n\n"
        f"Introduction:\n"
        f"{company} operates in the {industry} industry with an estimated annual revenue of "
        f"${revenue:,.0f}. Based in {location}, they currently use the following products: {current_products}.\n\n"
    )

    analysis = (
        f"Data Analysis:\n"
        f"- Product usage is currently at {usage}%, indicating {'strong' if usage >= 70 else 'moderate'} adoption.\n"
        f"- Opportunities were identified based on product affinity, customer interactions, and industry benchmarks.\n\n"
    )

    recommendations = []
    for i, item in enumerate(scored_opportunities[:5]):  # Top 5 only
        recommendations.append(
            f"{i+1}. Recommend **{item['product']}** "
            f"(Score: {item['score']}%) — {item['rationale']}."
        )

    conclusion = (
        "\nConclusion:\n"
        "Based on the data analysis, these recommendations are expected to improve customer satisfaction and lifetime value. "
        "Targeted marketing campaigns and sales efforts should be focused on the suggested products above."
    )

    full_text = intro + analysis + "Recommendations:\n" + "\n".join(recommendations) + conclusion


    summary = summarizer(full_text, max_length=120, min_length=60, do_sample=False)[0]['summary_text']

    return {
        "report_text": full_text,
        "executive_summary": summary,
        "structured_recommendations": scored_opportunities[:5]
    }
