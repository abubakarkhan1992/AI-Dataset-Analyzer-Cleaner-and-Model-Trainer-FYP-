import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

def correlation_analysis(df):

    numeric_df = df.select_dtypes(include=np.number)

    if numeric_df.shape[1] < 2:
        return

    st.subheader("Correlation Heatmap")

    corr = numeric_df.corr()

    fig, ax = plt.subplots()
    sns.heatmap(corr, cmap="coolwarm", ax=ax)

    st.pyplot(fig)