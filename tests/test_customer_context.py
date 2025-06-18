from app.agents.customer_context import get_customer_context

print("=== CUSTOMER CONTEXT ===")
context = get_customer_context("C001", use_embedding=True)
for k, v in context.items():
    print(f"{k}: {v}")
