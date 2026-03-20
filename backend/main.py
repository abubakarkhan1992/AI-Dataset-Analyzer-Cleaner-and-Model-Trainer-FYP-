from fastapi import FastAPI, UploadFile, File, Form
import pandas as pd
import io

# Import your existing pure modules
from modules.missing_values import analyze_missing
from modules.duplicates import analyze_duplicates
from modules.outliers import analyze_outliers
from modules.inconsistency import detect_inconsistencies
from modules.imbalance import detect_imbalance
from modules.correlation import correlation_analysis
from modules.quality_score import compute_quality_score

app = FastAPI(title="Dataset Analyser API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Dataset Analyser API! The server is running successfully. You can test endpoints at http://localhost:8000/docs"}

@app.post("/analyze")
async def analyze_dataset(file: UploadFile = File(...)):
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))
        
    # Run modular functions
    missing = analyze_missing(df)
    duplicates = analyze_duplicates(df)
    outliers = analyze_outliers(df)
    inconsistencies = detect_inconsistencies(df)
    imbalance = detect_imbalance(df)
    correlation = correlation_analysis(df)
    
    score = compute_quality_score(missing, duplicates, outliers, len(inconsistencies))
    
    return {
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_metrics": missing,
        "duplicate_metrics": duplicates,
        "outlier_metrics": outliers,
        "inconsistencies": inconsistencies,
        "imbalance_metrics": imbalance,
        "correlation": correlation,
        "quality_score": score
    }
