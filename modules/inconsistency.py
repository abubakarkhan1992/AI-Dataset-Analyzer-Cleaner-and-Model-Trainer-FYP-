import pandas as pd
import streamlit as st

def detect_inconsistencies(df):

    st.subheader("Inconsistent Data Detection")

    issues = []

    for col in df.columns:

        if df[col].dtype == "object":

            values = df[col].dropna().astype(str)

            # Case inconsistency
            if values.str.lower().nunique() < values.nunique():
                issues.append(f"{col}: Case inconsistency detected")

            # Date detection
            parsed = pd.to_datetime(values, errors="coerce")
            if parsed.notnull().sum() > len(values) * 0.6:
                issues.append(f"{col}: Should be datetime")

    if issues:
        for i in issues:
            st.warning(i)
    else:
        st.success("No inconsistencies detected")

    return len(issues)