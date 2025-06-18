from typing import List, Dict
from collections import Counter


from transformers import pipeline
import re

# Threshold for frequent usage
USAGE_THRESHOLD = 70

# Hugging Face zero-shot classifier to identify product matches
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def normalize(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text.lower().strip())

def purchase_pattern_analysis(customer_profile: Dict, activity_log: List[Dict]) -> Dict:
    owned_products_raw = customer_profile.get("current_products", "")
    usage_percent = customer_profile.get("product_usage_percent", 0)

    # Step 1: Normalize owned products (list of strings)
    owned_products = [normalize(p) for p in owned_products_raw.split(",") if p.strip()]

    # Step 2: Extract all product SKUs from activity log
    interacted_skus = [normalize(log["product_sku"]) for log in activity_log]

    # Step 3: Identify frequent usage
    frequently_used_products = owned_products if usage_percent >= USAGE_THRESHOLD else []

    # Step 4: Identify SKUs that are interacted with but not part of owned products
    missing_opportunities = []
    for sku in interacted_skus:
        match_found = any(sku in prod or prod in sku for prod in owned_products)
        if not match_found:
            missing_opportunities.append(sku)


    if missing_opportunities and owned_products:
        enriched = []
        for sku in missing_opportunities:
            result = classifier(sku, owned_products)
            enriched.append({
                "sku": sku,
                "possible_match": result['labels'][0],
                "confidence": result['scores'][0]
            })
        return {
            "frequently_used_products": frequently_used_products,
            "missing_product_opportunities": enriched
        }

    return {
        "frequently_used_products": frequently_used_products,
        "missing_product_opportunities": list(set(missing_opportunities))
    }
