def analyze_duplicates(df):
    duplicates = int(df.duplicated().sum())
    percent = float(round(duplicates / len(df) * 100, 2))
    
    return {
        "duplicate_count": duplicates,
        "duplicate_percent": percent
    }