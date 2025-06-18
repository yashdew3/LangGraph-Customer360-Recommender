from typing import Dict, List
from transformers import pipeline

# Optional zero-shot classifier
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def score_opportunities(customer_profile: Dict,
                        purchase_analysis: Dict,
                        product_affinity: Dict,
                        activity_log: List[Dict]) -> Dict:

    industry = customer_profile.get("industry", "")
    usage_percent = customer_profile.get("product_usage_percent", 0)

    # Build candidate set from missing + related
    candidates = set()
    missing = [p['sku'] if isinstance(p, dict) else p for p in purchase_analysis["missing_product_opportunities"]]
    candidates.update(missing)

    for pair in product_affinity["related_products"]:
        candidates.update(pair["suggested"])

    # Normalize
    candidates = list(set([p.lower().strip() for p in candidates]))

    scored_list = []

    for product in candidates:
        score = 0
        rationale = []

        # Usage boost if frequent usage products exist
        if usage_percent >= 70:
            score += 30
            rationale.append("High product usage indicates engagement")

        # Activity log match
        for activity in activity_log:
            if product in activity["product_sku"].lower():
                if activity["activity_priority"].lower() == "high":
                    score += 20
                    rationale.append("High-priority activity on product SKU")
                elif activity["activity_priority"].lower() == "medium":
                    score += 10
                    rationale.append("Medium-priority activity on product SKU")

        # Affinity match boost
        for pair in product_affinity["related_products"]:
            if product in [p.lower() for p in pair["suggested"]]:
                score += 30
                rationale.append(f"Frequently purchased with {pair['base_product']}")

        # Industry alignment using Hugging Face classifier
        candidate_label = product.replace("_", " ")
        hf_result = classifier(candidate_label, [industry])
        if hf_result["labels"][0].lower() == industry.lower():
            score += 20
            rationale.append("Industry-aligned product suggestion")

        scored_list.append({
            "product": product.title(),
            "score": min(score, 100),  # Clamp to 100
            "rationale": "; ".join(rationale)
        })

    scored_list = sorted(scored_list, key=lambda x: -x["score"])
    return {"scored_opportunities": scored_list}
