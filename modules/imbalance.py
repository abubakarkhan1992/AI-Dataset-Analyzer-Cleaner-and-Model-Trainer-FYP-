import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def detect_imbalance(df):

    st.subheader("Class Imbalance Detection")

    target = st.selectbox("Select Target Column", df.columns)

    unique_vals = df[target].nunique()

    if unique_vals > 20:
        st.warning("Not a classification column")
        return {"imbalance": 0}

    counts = df[target].value_counts()
    percentages = round((counts / counts.sum()) * 100, 1)

    st.dataframe(counts.reset_index().rename(columns={"index":"Class", target:"Count"}))

    ratio_str = " : ".join([f"{round(p,1)}%" for p in percentages])
    st.write("Class Ratio:", ratio_str)

    fig, ax = plt.subplots()
    sns.barplot(x=counts.index.astype(str), y=counts.values, ax=ax)
    st.pyplot(fig)

    return {"imbalance": percentages.max()}