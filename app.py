import streamlit as st
import pandas as pd
import requests
import json
from io import StringIO

# ================= CONFIG =================
FASTAPI_URL = "https://fastapi-for-fyp-1.onrender.com"

st.set_page_config(page_title="AutoML App", layout="wide")

# ================= SESSION STATE =================
if "df" not in st.session_state:
    st.session_state.df = None

if "cleaned_df" not in st.session_state:
    st.session_state.cleaned_df = None

if "training_results" not in st.session_state:
    st.session_state.training_results = None


# ================= TITLE =================
st.title("⚙️ AI Dataset Analyzer, Cleaner & AutoML Trainer")

# ================= FILE UPLOAD =================
uploaded_file = st.file_uploader("Upload Dataset", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.df = df

    st.subheader("📊 Dataset Preview")
    st.dataframe(df.head(), use_container_width=True)


# ================= WORKFLOW =================
option = st.radio(
    "Choose a workflow",
    ["Analysis", "Cleaning", "Training"],
    horizontal=True
)


# =========================================================
# ======================= ANALYSIS =========================
# =========================================================
if option == "Analysis" and st.session_state.df is not None:

    st.subheader("📊 Dataset Analysis")

    if st.button("Run Analysis"):

        files = {
            "file": ("data.csv", st.session_state.df.to_csv(index=False))
        }

        try:
            response = requests.post(f"{FASTAPI_URL}/analyze", files=files)

            if response.status_code == 200:
                result = response.json()
                st.json(result)
            else:
                st.error(f"Analysis failed: {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"Error connecting to API: {str(e)}")


# =========================================================
# ======================= CLEANING =========================
# =========================================================
if option == "Cleaning" and st.session_state.df is not None:

    st.subheader("🧹 Data Cleaning")

    target_column = st.selectbox(
        "Select Target Column",
        st.session_state.df.columns
    )

    if st.button("Clean Dataset"):

        files = {
            "file": ("data.csv", st.session_state.df.to_csv(index=False))
        }

        data = {
            "target_col": target_column
        }

        try:
            response = requests.post(
                f"{FASTAPI_URL}/clean",
                files=files,
                data=data
            )

            if response.status_code == 200:
                result = response.json()

                cleaned_csv = result.get("cleaned_data")

                if cleaned_csv:
                    cleaned_df = pd.read_csv(StringIO(cleaned_csv))
                    st.session_state.cleaned_df = cleaned_df

                    st.success("✅ Cleaning completed")

                    st.subheader("Cleaned Data Preview")
                    st.dataframe(cleaned_df.head(), use_container_width=True)

                    st.download_button(
                        "Download Cleaned CSV",
                        cleaned_df.to_csv(index=False),
                        "cleaned_data.csv",
                        "text/csv"
                    )
                else:
                    st.error("No cleaned data returned")

            else:
                st.error(f"Cleaning failed: {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"Error connecting to API: {str(e)}")


# =========================================================
# ======================= TRAINING =========================
# =========================================================
if option == "Training":

    st.subheader("🤖 Model Training with AutoML")

    df_to_use = (
        st.session_state.cleaned_df
        if st.session_state.cleaned_df is not None
        else st.session_state.df
    )

    if df_to_use is None:
        st.warning("Please upload dataset first")
        st.stop()

    target_column = st.selectbox(
        "Target Column",
        df_to_use.columns
    )

    if st.button("🚀 Train Model"):

        st.info("Training... This may take a moment.")

        files = {
            "file": ("data.csv", df_to_use.to_csv(index=False))
        }

        data = {
            "target_col": target_column
        }

        try:
            response = requests.post(
                f"{FASTAPI_URL}/train",
                files=files,
                data=data
            )

            if response.status_code == 200:
                result = response.json()

                st.session_state.training_results = result

                st.success("✅ Model Trained Successfully")

                # Display results
                training_results = result.get("training_results", {})

                st.subheader("🏆 Best Model")
                st.write(training_results.get("best_model"))

                st.subheader("📊 Model Metrics")
                st.json(training_results.get("model_metrics"))

            else:
                st.error(f"Training failed: {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"Error connecting to API: {str(e)}")
