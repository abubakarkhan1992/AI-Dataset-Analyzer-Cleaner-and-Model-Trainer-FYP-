import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import io
import json
from pathlib import Path

from modules.load_and_preview import load_data, show_preview

# ==================== CONFIGURATION ====================
# Updated to point to your live Render FastAPI backend
FASTAPI_URL = "https://fastapi-for-fyp-1.onrender.com"

st.set_page_config(page_title="AI Dataset Analyser and Trainer", layout="wide")
st.title("🔍 AI Dataset Analyser and Trainer")

# ==================== BACKEND WAKE-UP CHECK ====================
# Since Render Free Tier sleeps, we check if the backend is awake
@st.cache_data(ttl=60)
def check_backend():
    try:
        response = requests.get(f"{FASTAPI_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

if not check_backend():
    st.warning("⚠️ The AI Backend is currently 'sleeping' (Render Free Tier). It may take up to 60 seconds to start. Please wait or refresh the page shortly.")

# ==================== SESSION STATE ====================
if "manual_results" not in st.session_state:
    st.session_state.manual_results = None
if "profile_results" not in st.session_state:
    st.session_state.profile_results = None
if "current_df" not in st.session_state:
    st.session_state.current_df = None

# ==================== SIDEBAR & UPLOAD ====================
uploaded_file = st.sidebar.file_uploader("Upload Dataset", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        st.session_state.current_df = df
        st.success("✅ Dataset Loaded Successfully")
        show_preview(df, uploaded_file)
        
        st.subheader("⚙️ Module Options")
        main_option = st.radio(
            "Choose a workflow",
            ["Analysis", "Cleaning", "Training"],
            horizontal=True,
            key="main_option"
        )

        if main_option == "Analysis":
            st.subheader("📊 Analysis Options")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔍 Manual Quality Analysis", key="manual_btn"):
                    with st.spinner("Analyzing dataset..."):
                        uploaded_file.seek(0)
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), 
                                 "text/csv" if uploaded_file.name.endswith('.csv') else 
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

                        try:
                            response = requests.post(f"{FASTAPI_URL}/analyze", files=files)
                            response.raise_for_status()
                            st.session_state.manual_results = response.json()
                            st.success("✅ Manual analysis complete!")
                        except requests.exceptions.RequestException as e:
                            st.error(f"❌ Connection Error: Ensure backend is awake at {FASTAPI_URL}")

            with col2:
                if st.button("📈 Automated Profiling (ydata)", key="profile_btn"):
                    with st.spinner("Generating profile..."):
                        uploaded_file.seek(0)
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), 
                                 "text/csv" if uploaded_file.name.endswith('.csv') else 
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

                        try:
                            response = requests.post(f"{FASTAPI_URL}/profile", files=files)
                            response.raise_for_status()
                            st.session_state.profile_results = response.json()
                            st.success("✅ Automated profiling complete!")
                        except requests.exceptions.RequestException as e:
                            st.error(f"❌ Failed to generate profile: {e}")

            tab1, tab2 = st.tabs(["📋 Manual Analysis", "📊 Automated Profile"])

            # --- TAB 1: MANUAL ANALYSIS ---
            with tab1:
                if st.session_state.manual_results:
                    results = st.session_state.manual_results
                    col_dl1, col_dl2, col_dl3 = st.columns([2, 2, 4])
                    
                    with col_dl1:
                        if st.button("⬇️ Download JSON Report", key="dl_manual"):
                            try:
                                uploaded_file.seek(0)
                                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv" if uploaded_file.name.endswith('.csv') else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                                response = requests.post(f"{FASTAPI_URL}/analyze/download", files=files)
                                response.raise_for_status()
                                st.download_button(label="💾 Save JSON", data=response.content, file_name=f"manual_report_{Path(uploaded_file.name).stem}.json", mime="application/json")
                            except Exception as e: st.error(f"Error: {e}")

                    with col_dl2:
                        if st.button("⬇️ Download PDF Report", key="dl_manual_pdf"):
                            try:
                                uploaded_file.seek(0)
                                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv" if uploaded_file.name.endswith('.csv') else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                                response = requests.post(f"{FASTAPI_URL}/analyze/download/pdf", files=files)
                                response.raise_for_status()
                                st.download_button(label="💾 Save PDF", data=response.content, file_name=f"manual_report_{Path(uploaded_file.name).stem}.pdf", mime="application/pdf")
                            except Exception as e: st.error(f"Error: {e}")

                    st.header("📊 Data Quality Analysis Results")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1: st.metric("📊 Total Rows", results["rows"])
                    with col2: st.metric("📋 Total Columns", results["columns"])
                    with col3: st.metric("⚠️ Quality Score", f"{results['quality_score']}/10")
                    with col4: st.metric("🏆 Remarks", "Excellent" if results['quality_score'] >= 8 else "Good" if results['quality_score'] >= 7 else "Average" if results['quality_score'] >= 6 else "Poor")

                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("🔍 Missing Values")
                        m_data = results["missing_metrics"]
                        m_df = pd.DataFrame({"Count": m_data["missing_count"], "Percentage (%)": m_data["missing_percent"]})
                        m_cols = m_df[m_df["Count"] > 0]
                        if not m_cols.empty: st.dataframe(m_cols, use_container_width=True)
                        else: st.success("✅ No missing values found!")

                    with col2:
                        st.subheader("♻️ Duplicate Detection")
                        dupes = results["duplicate_metrics"]["duplicate_count"]
                        st.write(f"**Duplicate Rows:** {dupes} ({results['duplicate_metrics']['duplicate_percent']}%)")
                        if dupes > 0 and st.checkbox("Show duplicate rows"):
                            st.dataframe(st.session_state.current_df[st.session_state.current_df.duplicated()].head(50))

                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📈 Outlier Detection")
                        if results["outlier_metrics"]["outlier_counts"]:
                            st.write(f"**Overall Outlier Ratio:** {round(results['outlier_metrics']['outlier_ratio'], 2)}%")
                            st.dataframe(pd.DataFrame([results["outlier_metrics"]["outlier_counts"]]).T.rename(columns={0: "Count"}), use_container_width=True)
                        else: st.info("No outliers detected.")
                    with col2:
                        st.subheader("⚙️ Data Inconsistencies")
                        if results["inconsistencies"]: st.dataframe(pd.DataFrame(results["inconsistencies"]), use_container_width=True)
                        else: st.success("✅ No inconsistencies detected!")

                    st.divider()
                    st.subheader("🔗 Correlation Matrix")
                    if results["correlation"]["matrix"]:
                        fig, ax = plt.subplots(figsize=(10, 8))
                        sns.heatmap(pd.DataFrame(results["correlation"]["matrix"]), cmap="coolwarm", annot=True, fmt=".2f", ax=ax)
                        st.pyplot(fig)
                else:
                    st.info("📌 Run 'Manual Quality Analysis' to begin.")

            # --- TAB 2: AUTOMATED PROFILING ---
            with tab2:
                if st.session_state.profile_results:
                    prof_results = st.session_state.profile_results
                    if st.button("⬇️ Download Profile (HTML)", key="dl_profile"):
                        try:
                            uploaded_file.seek(0)
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv" if uploaded_file.name.endswith('.csv') else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                            response = requests.post(f"{FASTAPI_URL}/profile/download", files=files)
                            st.download_button(label="💾 Save HTML Report", data=response.content, file_name=f"data_profile_{Path(uploaded_file.name).stem}.html", mime="text/html")
                        except Exception as e: st.error(f"Error: {e}")
                    
                    st.header("📊 Profile Summary")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Rows", prof_results["rows"])
                    c2.metric("Cols", prof_results["columns"])
                    c3.metric("Missing", prof_results["missing_cells"])
                    c4.metric("Duplicates", prof_results["duplicate_rows"])
                else:
                    st.info("📌 Run 'Automated Profiling' to generate report.")

        elif main_option == "Cleaning":
            st.subheader("🧹 Cleaning Options")
            t_man, t_auto = st.tabs(["🧹 Manual", "🤖 Automated"])
            
            with t_man:
                c1, c2, c3 = st.columns(3)
                with c1:
                    mv_opt = st.selectbox("Missing Values", ["None", "Drop missing values", "Standard Imputation (Mean/Mode)", "Robust Imputation (Median/Mode)"])
                    dup_opt = st.selectbox("Duplicates", ["None", "Keep First", "Keep Last", "Drop All"])
                with c2:
                    inc_opt = st.selectbox("Inconsistencies", ["None", "Standardize (Lower & Strip)"])
                    enc_opt = st.selectbox("Encoding", ["None", "Label Encoding", "One-Hot Encoding"])
                with c3:
                    imb_opt = st.selectbox("Class Imbalance", ["None", "Undersample to balance"])
                    imb_target = st.selectbox("Target Col", list(st.session_state.current_df.columns)) if imb_opt != "None" else "None"

                if st.button("🚀 Run Manual Cleaning"):
                    config = {"missing_values": mv_opt, "duplicates": dup_opt, "imbalance": imb_opt, "imbalance_target": imb_target, "inconsistencies": inc_opt, "encoding": enc_opt}
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    data = {"config": json.dumps(config)}
                    response = requests.post(f"{FASTAPI_URL}/clean/manual", files=files, data=data)
                    if response.ok:
                        st.download_button("⬇️ Download Cleaned Data", response.content, f"cleaned_{uploaded_file.name}")

            with t_auto:
                target_col_auto = st.selectbox("Select Target Column", list(st.session_state.current_df.columns))
                if st.button("🚀 Run Automated Cleaning"):
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    response = requests.post(f"{FASTAPI_URL}/clean/auto", files=files, data={"target_col": target_col_auto})
                    if response.ok:
                        st.download_button("⬇️ Download Auto-Cleaned Data", response.content, f"autocleaned_{uploaded_file.name}")

        else:
            st.subheader("🤖 Model Training with AutoML")
            target_column = st.selectbox("Target Column", list(st.session_state.current_df.columns), key="target_col_training")
            
            if st.button("🚀 Train Model", use_container_width=True):
                with st.spinner("Training... This may take a moment."):
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    response = requests.post(f"{FASTAPI_URL}/train", files=files, data={"target_col": target_column})
                    if response.ok:
                        result = response.json()
                        st.session_state.training_results = result
                        st.session_state.trained_model_id = result.get("model_id")
                        st.success(f"Model Trained: {result['training_results']['best_model']}")
            
            if st.session_state.get("training_results"):
                mid = st.session_state.trained_model_id
                if st.button("⬇️ Download Model (Pickle)"):
                    res = requests.get(f"{FASTAPI_URL}/train/download/{mid}")
                    st.download_button("💾 Save .pkl File", res.content, f"model_{mid}.pkl")

else:
    st.info("📤 Upload a dataset to begin analysis!")
