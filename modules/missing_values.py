import pandas as pd
import streamlit as st

def analyze_missing(df):

    missing_count = df.isnull().sum()
    missing_percent = round((missing_count / len(df)) * 100, 2)

    result = pd.DataFrame({
        "Missing Count": missing_count,
        "Missing %": missing_percent
    })

    st.subheader("Missing Values")
    st.dataframe(result)

    return {
        "missing_percent_mean": missing_percent.mean()
    }