import streamlit as st
import requests

# Set page config
st.set_page_config(page_title="Customer 360° Recommender", layout="centered")

st.title("📊 Customer 360° Recommendation Engine")
st.caption("Powered by LangGraph & FastAPI")

# Input
customer_id = st.text_input("Enter Customer ID (e.g., C001)", value="C001")

if st.button("🔍 Generate Report"):
    with st.spinner("Generating insights..."):
        try:
            res = requests.get(f"http://localhost:8000/recommendation?customer_id={customer_id}")
            data = res.json()

            if "error" in data:
                st.error(data["error"])
            else:
                # Executive Summary
                st.subheader("📌 Executive Summary")
                st.success(data["executive_summary"])

                # Recommendations
                st.subheader("📦 Top Product Recommendations")
                for item in data["structured_recommendations"]:
                    with st.expander(f"{item['product']} — {item['score']}% match"):
                        st.markdown(f"**Rationale:** {item['rationale']}")

                # Full Report
                with st.expander("📄 Full Research Report"):
                    st.text(data["report_text"])

        except Exception as e:
            st.error(f"Failed to fetch report: {e}")
