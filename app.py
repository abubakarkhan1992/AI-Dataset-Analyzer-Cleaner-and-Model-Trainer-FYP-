import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

from modules.load_and_preview import load_data, show_preview

FASTAPI_URL = "http://localhost:8000/analyze"

st.set_page_config(page_title="AI Dataset Quality Auditor", layout="wide")
st.title("🔍 AI Dataset Quality Auditor")

# Initialize session state for persistent results
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

# Sidebar upload
uploaded_file = st.sidebar.file_uploader("Upload Dataset", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        st.success("Dataset Loaded Successfully")
        show_preview(df, uploaded_file)
        
        if st.button("Start Data Quality Analysis"):
            with st.spinner("Analyzing dataset on the backend..."):
                # Rewind file pointer
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv" if uploaded_file.name.endswith('.csv') else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                
                try:
                    response = requests.post(FASTAPI_URL, files=files)
                    response.raise_for_status()
                    # Store results in session state so interaction doesn't wipe them!
                    st.session_state.analysis_results = response.json()
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to connect to backend: {e}")
                    st.session_state.analysis_results = None
                    
        # If we have results, render the UI (this stays active even if dropdowns are clicked!)
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            st.header("📊 Data Quality Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Missing Values")
                missing_df = pd.DataFrame({
                    "Count": results["missing_metrics"]["missing_count"],
                    "Percentage (%)": results["missing_metrics"]["missing_percent"]
                })
                st.dataframe(missing_df[missing_df["Count"] > 0])
                if missing_df["Count"].sum() == 0:
                    st.info("No missing values found.")
                
                st.subheader("Duplicate Detection")
                dupes = results["duplicate_metrics"]["duplicate_count"]
                dupe_pct = results["duplicate_metrics"]["duplicate_percent"]
                st.write(f"Duplicate Rows: **{dupes}** ({dupe_pct}%)")
                
                if dupes > 0:
                    st.write("Preview of duplicated rows:")
                    # Display the actual duplicated rows locally
                    st.dataframe(df[df.duplicated(keep=False)].sort_values(by=list(df.columns)).head(50))
            
            with col2:
                st.subheader("Outlier Detection")
                outliers = results["outlier_metrics"]["outlier_counts"]
                outlier_ratio = results["outlier_metrics"]["outlier_ratio"]
                if outliers:
                    st.write(f"Overall Outlier Ratio: **{round(outlier_ratio, 2)}%**")
                    st.dataframe(pd.DataFrame([outliers]).T.rename(columns={0: "Outlier Count"}).sort_values("Outlier Count", ascending=False))
                else:
                    st.info("No numerical outliers detected.")
                    
            st.subheader("Inconsistent Data Detection")
            inconsistencies = results["inconsistencies"]
            if inconsistencies:
                # Convert list of dicts to dataframe for beautiful rendering
                inc_df = pd.DataFrame(inconsistencies)
                st.dataframe(inc_df, use_container_width=True)
            else:
                st.success("No inconsistencies detected")
                
            st.subheader("Class Imbalance Detection")
            imbalances = results["imbalance_metrics"]
            if imbalances:
                # Let user pick inside this section!
                target_col = st.selectbox("Select Target Column to view imbalance", ["None"] + list(imbalances.keys()))
                
                if target_col != "None":
                    data = imbalances[target_col]
                    st.write(f"Max class percentage: **{data['imbalance_score']}%**")
                    
                    # Show as beautiful dataframe
                    count_df = pd.DataFrame({
                        "Class": list(data["counts"].keys()),
                        "Count": list(data["counts"].values()),
                        "Percentage (%)": list(data["percentages"].values())
                    })
                    st.dataframe(count_df)
                    
                    # Optional bar chart
                    st.bar_chart(count_df.set_index("Class")["Count"])
            else:
                st.info("No categorical columns suitable for classification found.")
            
            st.subheader("Correlation Matrix")
            matrix = results["correlation"]["matrix"]
            if matrix:
                corr_df = pd.DataFrame(matrix)
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(corr_df, cmap="coolwarm", annot=False, ax=ax)
                st.pyplot(fig)
            else:
                st.info("Not enough numeric columns for correlation.")
                
            st.subheader("🏆 Final Dataset Quality Score")
            st.metric("Score", f"{results['quality_score']}/10")
            
else:
    # Clear session state if a new file isn't uploaded
    st.session_state.analysis_results = None
    st.info("Upload a dataset to begin.")
