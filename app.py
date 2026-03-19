import streamlit as st
import pandas as pd

# Import modules
from modules.load_and_preview import load_data, show_preview
from modules.missing_values import analyze_missing
from modules.duplicates import analyze_duplicates
from modules.outliers import analyze_outliers
from modules.inconsistency import detect_inconsistencies, display_inconsistencies
from modules.imbalance import detect_imbalance
from modules.correlation import correlation_analysis
from modules.quality_score import compute_quality_score

st.set_page_config(page_title="AI Dataset Quality Auditor", layout="wide")

st.title("🔍 AI Dataset Quality Auditor")

# Session state for analysis persistence
if "analysis_started" not in st.session_state:
    st.session_state.analysis_started = False

# Sidebar upload
uploaded_file = st.sidebar.file_uploader("Upload Dataset", type=["csv", "xlsx"])

if uploaded_file:

    df = load_data(uploaded_file)

    st.success("Dataset Loaded Successfully")

    show_preview(df, uploaded_file)

    if st.button("Start Data Quality Analysis"):
        st.session_state.analysis_started = True

    if st.session_state.analysis_started:

        st.header("📊 Data Quality Analysis")

        # Missing Values
        missing_metrics = analyze_missing(df)

        # Duplicates
        duplicate_metrics = analyze_duplicates(df)

        # Inconsistencies
        issues = display_inconsistencies(df)
        inconsistency_count = len(issues)

        # Outliers
        outlier_metrics = analyze_outliers(df)

        # Correlation
        correlation_analysis(df)

        # Imbalance
        imbalance_metrics = detect_imbalance(df)

        # Quality Score
        score = compute_quality_score(
            missing_metrics,
            duplicate_metrics,
            outlier_metrics,
            inconsistency_count
        )

        st.subheader("🏆 Final Dataset Quality Score")
        st.metric("Score", f"{score}/10")

else:
    st.info("Upload a dataset to begin.")