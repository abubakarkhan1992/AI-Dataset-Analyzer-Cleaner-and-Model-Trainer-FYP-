def compute_quality_score(missing, duplicates, outliers, inconsistencies):

    completeness = 100 - missing["missing_percent_mean"]
    uniqueness = 100 - duplicates["duplicate_percent"]
    outlier_score = 100 - outliers["outlier_ratio"]

    consistency = max(0, 100 - inconsistencies * 5)

    score = (
        completeness * 0.3 +
        uniqueness * 0.2 +
        outlier_score * 0.3 +
        consistency * 0.2
    ) / 10

    return round(score, 2)