import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

def analyze_outliers(df):

    numeric_df = df.select_dtypes(include=np.number).copy()

    # Remove ID-like columns
    cols_to_drop = []

    for col in numeric_df.columns:

        if "id" in col.lower():
            cols_to_drop.append(col)

        elif numeric_df[col].nunique() == len(df):
            cols_to_drop.append(col)

    numeric_df.drop(columns=cols_to_drop, inplace=True, errors="ignore")

    st.subheader("Outlier Detection")

    # Case 1: No numeric columns left
    if numeric_df.empty:
        st.info("No outliers detected.")
        return {"outlier_ratio": 0}

    outlier_counts = {}
    outlier_columns = []

    for col in numeric_df.columns:

        Q1 = numeric_df[col].quantile(0.25)
        Q3 = numeric_df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        mask = (numeric_df[col] < lower) | (numeric_df[col] > upper)
        count = mask.sum()

        outlier_counts[col] = count

        if count > 0:
            outlier_columns.append(col)

    # Always show table
    outlier_df = pd.DataFrame.from_dict(
        outlier_counts,
        orient="index",
        columns=["Outlier Count"]
    )

    st.dataframe(outlier_df)

    # Case 2: No outliers found
    if not outlier_columns:
        st.success("No outliers detected in numeric columns.")
        return {"outlier_ratio": 0}

    # Case 3: Show boxplot if outliers exist
    st.subheader("Outlier Visualization (Boxplot)")

    fig, ax = plt.subplots(figsize=(10,6))
    sns.boxplot(data=numeric_df[outlier_columns], ax=ax)
    plt.xticks(rotation=45)

    st.pyplot(fig)

    # Calculate ratio
    total_outliers = sum(outlier_counts.values())
    total_values = numeric_df.size

    ratio = (total_outliers / total_values) * 100 if total_values > 0 else 0

    return {"outlier_ratio": ratio}