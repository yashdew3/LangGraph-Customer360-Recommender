from app.db import fetch_customer_profile, fetch_customer_activities

print("=== Customer Profile ===")
print(fetch_customer_profile("C001"))

print("\n=== Customer Activities ===")
print(fetch_customer_activities("C001"))
