import streamlit as st
import requests
import pandas as pd
import altair as alt

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="SmartFlow – Data Quality Assurance",
    layout="wide"
)

# ---------------- GLOBAL CSS (VIEW ONLY) ----------------
st.markdown(
    """
    <style>
    /* ---- Sticky Sidebar ---- */
    section[data-testid="stSidebar"] {
        position: sticky;
        top: 0;
        height: 100vh;
    }

    /* ---- Metric Card Styling ---- */
    div[data-testid="metric-container"] {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
    }

    div[data-testid="metric-container"] label {
        font-size: 0.85rem;
        color: #94a3b8;
    }

    /* ---- Success / Normal ---- */
    .metric-success div[data-testid="metric-container"] {
        border-left: 6px solid #22c55e;
    }

    /* ---- Anomaly / Warning ---- */
    .metric-warning div[data-testid="metric-container"] {
        border-left: 6px solid #f59e0b;
    }

    /* ---- Rejected / Error ---- */
    .metric-error div[data-testid="metric-container"] {
        border-left: 6px solid #ef4444;
    }

    /* ---- Neutral ---- */
    .metric-neutral div[data-testid="metric-container"] {
        border-left: 6px solid #3b82f6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- HELPERS ----------------
def status_badge(status: str):
    if status == "SUCCESS":
        st.success("Status: APPROVED")
    else:
        st.error("Status: REJECTED")

# ---------------- MAIN APP ----------------
def main():
    st.title("SmartFlow – Data Quality Pipeline")
    st.caption("LLM-powered ingestion with deterministic validation and anomaly detection")

    # -------- SIDEBAR --------
    with st.sidebar:
        with st.container(border=True):
            st.subheader("Controls")
            if st.button("Refresh Dashboard", use_container_width=True):
                st.rerun()

        with st.container(border=True):
            st.subheader("Input Format")
            st.code("Sold [Qty] [Item] to [Client]", language="text")

    tab1, tab2 = st.tabs(["Data Entry", "Live Dashboard"])

    # ================= TAB 1 =================
    with tab1:
        with st.container(border=True):
            st.subheader("Transaction Input")

            col_input, col_preview = st.columns([1.6, 1], gap="large")

            with col_input:
                raw_text = st.text_area(
                    "Transaction Text",
                    height=150,
                    placeholder="Example: Sold 5 iPhone 15s to Client A"
                )

                if st.button("Process Transaction", use_container_width=True, type="primary"):
                    if not raw_text.strip():
                        st.warning("Transaction text is required.")
                        return

                    with st.spinner("AI parsing, validating, and scoring..."):
                        res = requests.post(
                            f"{API_URL}/process/",
                            json={"text": raw_text},
                            timeout=10
                        )

                        if res.status_code != 200:
                            st.error(f"Backend Error ({res.status_code})")
                            return

                        result = res.json()
                        status_badge(result["status"])

                        if result["status"] == "SUCCESS":
                            d = result["data"]

                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.markdown('<div class="metric-neutral">', unsafe_allow_html=True)
                                st.metric("Item", result["logs"]["parsed_json"]["item"])
                                st.markdown('</div>', unsafe_allow_html=True)

                            with c2:
                                st.markdown('<div class="metric-neutral">', unsafe_allow_html=True)
                                st.metric("Quantity", d["quantity"])
                                st.markdown('</div>', unsafe_allow_html=True)

                            with c3:
                                st.markdown('<div class="metric-neutral">', unsafe_allow_html=True)
                                st.metric("Total Value", f"${d['total_price']}")
                                st.markdown('</div>', unsafe_allow_html=True)

                            if d["is_flagged"]:
                                st.markdown('<div class="metric-warning">', unsafe_allow_html=True)
                                st.warning(f"Anomaly detected (Score: {d['anomaly_score']:.4f})")
                                st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="metric-success">', unsafe_allow_html=True)
                                st.success(f"Transaction within normal range (Score: {d['anomaly_score']:.4f})")
                                st.markdown('</div>', unsafe_allow_html=True)

                            with st.expander("View Full JSON Payload"):
                                st.json(result)
                        else:
                            st.markdown('<div class="metric-error">', unsafe_allow_html=True)
                            st.error(result.get("error", "Validation failed"))
                            st.markdown('</div>', unsafe_allow_html=True)

            with col_preview:
                with st.container(border=True):
                    st.subheader("System Flow")
                    st.markdown(
                        """
                        1. Entity extraction via LLM  
                        2. Referential validation in SQL  
                        3. Business rule enforcement  
                        4. Anomaly scoring via ML  
                        """
                    )

                if raw_text:
                    with st.container(border=True):
                        st.subheader("Live Preview")
                        st.code(raw_text, language="text")

    # ================= TAB 2 =================
    with tab2:
        with st.container(border=True):
            st.subheader("Database Transactions")

            res = requests.get(f"{API_URL}/transactions/", timeout=5)
            if res.status_code != 200:
                st.warning("Unable to fetch transactions from backend.")
                return

            data = res.json()
            if not data:
                st.info("No transactions found in database.")
                return

            df = pd.DataFrame(data)
            df["status"] = "SUCCESS"

            k1, k2, k3 = st.columns(3)
            with k1:
                st.markdown('<div class="metric-neutral">', unsafe_allow_html=True)
                st.metric("Total Records", len(df))
                st.markdown('</div>', unsafe_allow_html=True)

            with k2:
                st.markdown('<div class="metric-success">', unsafe_allow_html=True)
                st.metric("Approved", len(df))
                st.markdown('</div>', unsafe_allow_html=True)

            with k3:
                st.markdown('<div class="metric-error">', unsafe_allow_html=True)
                st.metric("Rejected", "0")
                st.markdown('</div>', unsafe_allow_html=True)

            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "anomaly_score": st.column_config.ProgressColumn(
                        "Anomaly Score",
                        min_value=-0.5,
                        max_value=0.5,
                        format="%.4f"
                    ),
                    "total_price": st.column_config.NumberColumn(
                        "Total Price",
                        format="$%.2f"
                    )
                }
            )

            st.subheader("Anomaly Score Distribution")
            chart = (
                alt.Chart(df)
                .mark_bar(color="#22c55e")
                .encode(
                    x=alt.X("anomaly_score:Q", bin=alt.Bin(maxbins=20)),
                    y=alt.Y("count()")
                )
                .properties(height=320)
            )
            st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()
