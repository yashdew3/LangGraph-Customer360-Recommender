import pandas as pd
import os
from typing import List, Dict
from transformers import AutoTokenizer, AutoModel
import torch

CATALOG_PATH = "data/product_catalog.csv"
HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Load embedding model
tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
model = AutoModel.from_pretrained(HF_MODEL)

def embed(text: str):
    tokens = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        embedding = model(**tokens).last_hidden_state.mean(dim=1)
    return embedding

def cosine_similarity(vec1, vec2):
    return torch.nn.functional.cosine_similarity(vec1, vec2).item()

def product_affinity_analysis(current_products: List[str]) -> Dict:
    df = pd.read_csv(CATALOG_PATH)
    df["product"] = df["product"].str.lower()
    
    suggestions = []

    for prod in current_products:
        prod_norm = prod.strip().lower()
        matches = df[df["product"] == prod_norm]

        if not matches.empty:
            related = matches.iloc[0]["related_products"]
            related_list = [p.strip() for p in related.split(",")]
        else:
            # Use embeddings if no match in catalog
            base_emb = embed(prod_norm)
            all_products = df["product"].tolist()
            similarities = []
            for alt_prod in all_products:
                alt_emb = embed(alt_prod)
                sim_score = cosine_similarity(base_emb, alt_emb)
                similarities.append((alt_prod, sim_score))
            related_list = [p for p, score in sorted(similarities, key=lambda x: -x[1])[:2]]

        suggestions.append({
            "base_product": prod,
            "suggested": related_list
        })

    return {"related_products": suggestions}
