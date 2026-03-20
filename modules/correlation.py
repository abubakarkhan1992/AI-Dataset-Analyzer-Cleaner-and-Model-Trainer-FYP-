import numpy as np

def correlation_analysis(df):
    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.shape[1] < 2:
        return {"matrix": {}}
        
    corr = numeric_df.corr().round(2)
    # Convert correlation matrix index and columns to string to ensure JSON serialization
    corr.index = corr.index.astype(str)
    corr.columns = corr.columns.astype(str)
    
    return {"matrix": corr.to_dict()}