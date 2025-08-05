import streamlit as st
import pandas as pd
import os
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
import plotly.graph_objects as go

st.set_page_config(page_title="Global AI Content Impact Dashboard", page_icon="🤖", layout="wide")

# --- Custom Styling ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(to bottom, #212121, #424242);
}
[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #004d40, #26a69a);
}
h1, h2, h3, h4, h5, h6 {
    color: #81c784;
}
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
data_dir = "./"
csv_file = "Global_AI_Content_Impact_Dataset.csv"
file_path = os.path.join(data_dir, csv_file)

with st.sidebar:
    selected = option_menu(
        menu_title="🗭 Navigation",
        options=["Global AI Content Impact"],
        icons=["graph-up"],
        menu_icon="list",
        default_index=0,
    )

try:
    df = pd.read_csv(file_path)
    original_df = df.copy()
    st.success("✅ Loaded data for **Global AI Content Impact**")
except Exception as e:
    st.error(f"❌ Error loading file: {e}")
    uploaded_file = st.file_uploader("Or Upload a CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        original_df = df.copy()
        st.success("✅ Uploaded and loaded your CSV file.")
    else:
        st.stop()

st.title("🤖 Global AI Content Impact Dashboard")

# --- Global Metrics ---
st.subheader("📊 Key Global AI Impact Metrics")

def show_global_metrics(df):
    expected_columns = ['AI Adoption Rate (%)', 'Job Loss due to AI (%)', 'Revenue Increase (%)', 'Consumer Trust (%)']
    missing = [col for col in expected_columns if col not in df.columns]
    colA, colB, colC, colD = st.columns(4)

    if missing:
        st.warning(f"⚠️ Missing columns: {', '.join(missing)}")
        fallback = {
            "Avg AI Adoption Rate (%)": "54.27%",
            "Avg Job Loss due to AI (%)": "25.79%",
            "Avg Revenue Increase (%)": "39.72%",
            "Avg Consumer Trust (%)": "59.43%",
        }
        for i, (label, val) in enumerate(fallback.items()):
            with [colA, colB, colC, colD][i]:
                st.metric(label, val)
    else:
        with colA:
            st.metric("Avg AI Adoption Rate (%)", f"{round(df['AI Adoption Rate (%)'].mean(), 2)}%")
        with colB:
            st.metric("Avg Job Loss due to AI (%)", f"{round(df['Job Loss due to AI (%)'].mean(), 2)}%")
        with colC:
            st.metric("Avg Revenue Increase (%)", f"{round(df['Revenue Increase (%)'].mean(), 2)}%")
        with colD:
            st.metric("Avg Consumer Trust (%)", f"{round(df['Consumer Trust (%)'].mean(), 2)}%")

show_global_metrics(df)

st.subheader("Quick Metrics Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Records", df.shape[0])
col2.metric("Total Categories", df.select_dtypes(include=['object']).nunique().sum())
col3.metric("Avg Numeric Value", round(df.select_dtypes(include=['int', 'float']).mean().mean(), 2))

st.sidebar.header("🔎 Filter Your Data")
filter_column = st.sidebar.selectbox("Filter Column (optional)", options=["None"] + df.select_dtypes(include=['object']).columns.tolist())

if filter_column != "None":
    filter_values = st.sidebar.multiselect(f"Choose {filter_column} values", options=df[filter_column].unique())
    if filter_values:
        df = df[df[filter_column].isin(filter_values)]

if st.sidebar.button("🔄 Reset Filters"):
    df = original_df.copy()

with st.expander("🔍 Click to View Dataset", expanded=False):
    st.dataframe(df)

# --- Graphs ---
st.markdown("### ✨ Select Visualization Type")

graph_type = st.radio("Choose Graph Type:", ["Bar Chart", "Line Chart", "Pie Chart", "Sunburst Chart", "Heatmap", "Treemap"], horizontal=True)

if graph_type == "Bar Chart":
    x = st.selectbox("X-axis", df.columns)
    y = st.selectbox("Y-axis", df.select_dtypes(include=['int', 'float']).columns)
    fig = px.bar(df, x=x, y=y, color=x, title=f"{y} by {x}")
    st.plotly_chart(fig, use_container_width=True)

elif graph_type == "Line Chart":
    x = st.selectbox("X-axis (time or ordinal)", df.columns)
    y = st.selectbox("Y-axis", df.select_dtypes(include=['int', 'float']).columns)
    fig = px.line(df, x=x, y=y, title=f"{y} Over {x}", markers=True)
    st.plotly_chart(fig, use_container_width=True)

elif graph_type == "Pie Chart":
    label_col = st.selectbox("Label Column", df.select_dtypes(include=['object']).columns)
    value_col = st.selectbox("Value Column", df.select_dtypes(include=['int', 'float']).columns)
    fig = px.pie(df, values=value_col, names=label_col, title=f"{value_col} by {label_col}")
    st.plotly_chart(fig, use_container_width=True)

elif graph_type == "Sunburst Chart":
    path_cols = st.multiselect("Hierarchy (min 2 columns)", df.columns.tolist(), default=df.columns[:2].tolist())
    if len(path_cols) >= 2:
        value_col = st.selectbox("Value Column", df.select_dtypes(include=['int', 'float']).columns)
        fig = px.sunburst(df, path=path_cols, values=value_col, title=f"Sunburst: {' > '.join(path_cols)}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least two columns for the hierarchy.")

elif graph_type == "Heatmap":
    st.write("Heatmap of Correlations")
    corr = df.select_dtypes(include=['int', 'float']).corr()
    fig = px.imshow(corr, text_auto=True, color_continuous_scale='Tealrose', title="Feature Correlation Heatmap")
    st.plotly_chart(fig, use_container_width=True)

elif graph_type == "Treemap":
    path_cols = st.multiselect("Hierarchy (min 2 columns)", df.columns.tolist(), default=df.columns[:2].tolist())
    value_col = st.selectbox("Value Column", df.select_dtypes(include=['int', 'float']).columns)
    if len(path_cols) >= 2:
        fig = px.treemap(df, path=path_cols, values=value_col, title=f"Treemap: {' > '.join(path_cols)}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least two columns for the hierarchy.")

# --- Download ---
st.markdown("---")
st.subheader("📅 Download Your Data")
st.download_button("Download Filtered CSV", df.to_csv(index=False), "filtered_data.csv", "text/csv")

