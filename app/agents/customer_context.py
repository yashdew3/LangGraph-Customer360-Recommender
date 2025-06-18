import pandas as pd
from app.db import fetch_customer_profile
import os

# Optional: Hugging Face embedding for customer description
from transformers import AutoTokenizer, AutoModel
import torch

HF_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def load_hf_model():
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
    model = AutoModel.from_pretrained(HF_MODEL_NAME)
    return tokenizer, model

def embed_text(text: str, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state.mean(dim=1)
    return embeddings.squeeze().tolist()


def clean_customer_data(row: dict) -> dict:
    return {
        "customer_id": row.get("customer_id"),
        "customer_name": row.get("customer_name"),
        "industry": row.get("industry"),
        "annual_revenue": row.get("annual_revenue"),
        "location": row.get("location"),
        "current_products": row.get("current_products"),
        "product_usage_percent": row.get("product_usage_percent"),
        "account_type": row.get("account_type"),
        "priority_rating": row.get("priority_rating"),
        "opportunity_stage": row.get("opportunity_stage"),
        "opportunity_amount": row.get("opportunity_amount"),
        "opportunity_type": row.get("opportunity_type"),
        "competitors": row.get("competitors")
    }

def get_customer_context(customer_id: str, use_embedding: bool = False) -> dict:
    try:
        row = fetch_customer_profile(customer_id)
        if not row:
            raise Exception("Customer not found in DB")
    except Exception as e:
        print(f"[DB FAILOVER] {e} → Loading from CSV.")
        df = pd.read_csv("data/customer_data.csv")
        row_df = df[df["customer_id"] == customer_id]
        if row_df.empty:
            return {"error": "Customer not found in DB or CSV"}
        row = row_df.iloc[0].to_dict()

    profile = clean_customer_data(row)

    # Optionally add HuggingFace embeddings
    if use_embedding:
        tokenizer, model = load_hf_model()
        text = f"{profile['industry']} - {profile['current_products']} - {profile['location']}"
        profile["embedding"] = embed_text(text, tokenizer, model)

    return profile
