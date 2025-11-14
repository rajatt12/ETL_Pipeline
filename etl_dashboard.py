import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Telecom ETL Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📶 Telecom ETL Dashboard")
st.caption("Visualizing customer usage, plan data, and derived analytics.")

@st.cache_data
def load_data():
    df = pd.read_csv("usage_plan_output.csv")   # same folder as script
    return df


try:
    data = load_data()
    st.success("✅ Data loaded successfully!")
except FileNotFoundError:
    st.error("⚠️ File not found! Run your ETL pipeline first to create 'usage_plan_output.csv'.")
    st.stop()


st.sidebar.header("🔍 Filters")

regions = sorted(data["region"].dropna().unique())
plan_types = sorted(data["plan_type"].dropna().unique())

selected_region = st.sidebar.multiselect("Select Region(s):", regions, default=regions)
selected_plan_type = st.sidebar.multiselect("Select Plan Type(s):", plan_types, default=plan_types)

filtered = data[
    data["region"].isin(selected_region) &
    data["plan_type"].isin(selected_plan_type)
]


st.markdown("### 📈 Summary Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Total Records", len(filtered))
col2.metric("Data Limit Exceeded", int(filtered["data_exceed_flag"].sum()))
col3.metric("Average Data Used (GB)", round(filtered["data_used_gb"].mean(), 2))


tab1, tab2, tab3 = st.tabs(["📊 Data Usage", "📞 Calls & SMS", "⚠️ Exceed Analysis"])

with tab1:
    st.markdown("#### Average Data Used by Region")
    avg_data = filtered.groupby("region")["data_used_gb"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(6,3))
    ax.bar(avg_data["region"], avg_data["data_used_gb"])
    ax.set_xlabel("Region")
    ax.set_ylabel("Avg Data Used (GB)")
    ax.set_title("Average Data Usage by Region")
    st.pyplot(fig)

with tab2:
    st.markdown("#### Average Calls and SMS by Plan Type")
    usage_summary = (
        filtered.groupby("plan_type")[["calls_made", "sms_sent"]].mean().reset_index()
    )

    st.bar_chart(usage_summary.set_index("plan_type"))

with tab3:
    st.markdown("#### Exceed Flag Summary")
    exceed_summary = {
        "Data Exceed": filtered["data_exceed_flag"].sum(),
        "Call Exceed": filtered["call_exceed_flag"].sum(),
        "SMS Exceed": filtered["sms_exceed_flag"].sum(),
    }
    st.bar_chart(pd.DataFrame.from_dict(exceed_summary, orient="index", columns=["Count"]))


with st.expander("📋 View Processed Data"):
    st.dataframe(filtered.head(50))

st.markdown("---")
st.caption("Built with ❤️ using Streamlit and Pandas.")
