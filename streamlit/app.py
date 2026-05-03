from __future__ import annotations

import streamlit as st


DATABASE = "ACTUARIAL_AI_DEV"


st.set_page_config(page_title="Valuation Movement", layout="wide")
st.title("Valuation Movement")


@st.cache_data(ttl=60)
def load_table(table_name: str):
    try:
        from snowflake.snowpark.context import get_active_session

        session = get_active_session()
        return session.table(table_name).to_pandas()
    except Exception as exc:
        st.warning(f"Snowflake table unavailable: {exc}")
        return None


summary = load_table(f"{DATABASE}.APP.DASHBOARD_SUMMARY")
validations = load_table(f"{DATABASE}.RUNS.VALIDATION_RESULTS")

if summary is None or summary.empty:
    st.info("No dashboard summary rows found. Run the Copilot valuation movement workflow first.")
    st.stop()

run_ids = sorted(summary["RUN_ID"].dropna().unique().tolist())
selected_run = st.selectbox("Run", run_ids, index=len(run_ids) - 1)
filtered = summary[summary["RUN_ID"] == selected_run]

products = sorted(filtered["PRODUCT"].dropna().unique().tolist())
product = st.multiselect("Product", products, default=products)
if product:
    filtered = filtered[filtered["PRODUCT"].isin(product)]

left, right = st.columns([2, 1])
with left:
    st.subheader("Movement by Driver")
    chart_data = filtered.groupby("DRIVER", as_index=False)["AMOUNT"].sum()
    st.bar_chart(chart_data, x="DRIVER", y="AMOUNT")

with right:
    st.subheader("Validation")
    if validations is not None and not validations.empty:
        run_validations = validations[validations["RUN_ID"] == selected_run]
        st.dataframe(run_validations[["CHECK_NAME", "STATUS", "SEVERITY", "MESSAGE"]], use_container_width=True)
    else:
        st.info("No validation rows found.")

st.subheader("Movement Detail")
st.dataframe(filtered, use_container_width=True)

