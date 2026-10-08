import pandas as pd


def analyze_quality(df):
    """
    Analyze suppliers based on:
    - Quality Score
    - Defect Rate
    - Past Performance Score
    """

    data = df.copy()

    # Quality Score:
    # Higher quality score = better supplier
    quality_min = data["Quality_Score"].min()
    quality_max = data["Quality_Score"].max()

    if quality_max == quality_min:
        data["Quality_Score_Normalized"] = 100
    else:
        data["Quality_Score_Normalized"] = (
            (data["Quality_Score"] - quality_min)
            / (quality_max - quality_min)
        ) * 100

    # Defect Score:
    # Lower defect rate = better supplier
    defect_min = data["Defect_Rate"].min()
    defect_max = data["Defect_Rate"].max()

    if defect_max == defect_min:
        data["Defect_Score"] = 100
    else:
        data["Defect_Score"] = (
            (defect_max - data["Defect_Rate"])
            / (defect_max - defect_min)
        ) * 100

    # Past Performance:
    # Higher score = better supplier
    performance_min = data["Past_Performance_Score"].min()
    performance_max = data["Past_Performance_Score"].max()

    if performance_max == performance_min:
        data["Performance_Score"] = 100
    else:
        data["Performance_Score"] = (
            (data["Past_Performance_Score"] - performance_min)
            / (performance_max - performance_min)
        ) * 100

    # Overall Quality Score
    data["Overall_Quality_Score"] = (
        data["Quality_Score_Normalized"] * 0.40
        + data["Defect_Score"] * 0.30
        + data["Performance_Score"] * 0.30
    )

    # Rank suppliers
    data["Quality_Rank"] = (
        data["Overall_Quality_Score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    # Best supplier from quality perspective
    best_supplier = data.loc[
        data["Overall_Quality_Score"].idxmax()
    ]

    # Lowest defect supplier
    lowest_defect_supplier = data.loc[
        data["Defect_Rate"].idxmin()
    ]

    result = {
        "supplier_analysis": data[
            [
                "Supplier_ID",
                "Supplier_Name",
                "Quality_Score",
                "Defect_Rate",
                "Past_Performance_Score",
                "Quality_Score_Normalized",
                "Defect_Score",
                "Performance_Score",
                "Overall_Quality_Score",
                "Quality_Rank"
            ]
        ].sort_values("Quality_Rank"),

        "best_quality_supplier": {
            "Supplier_ID": best_supplier["Supplier_ID"],
            "Supplier_Name": best_supplier["Supplier_Name"],
            "Quality_Score": best_supplier["Quality_Score"],
            "Defect_Rate": best_supplier["Defect_Rate"],
            "Overall_Quality_Score": round(
                best_supplier["Overall_Quality_Score"], 2
            )
        },

        "lowest_defect_supplier": {
            "Supplier_ID": lowest_defect_supplier["Supplier_ID"],
            "Supplier_Name": lowest_defect_supplier["Supplier_Name"],
            "Defect_Rate": lowest_defect_supplier["Defect_Rate"]
        }
    }

    return result


if __name__ == "__main__":

    df = pd.read_csv("data/supplier_data.csv")

    result = analyze_quality(df)

    print("\n===== QUALITY ANALYSIS =====\n")

    print(
        result["supplier_analysis"].to_string(index=False)
    )

    print("\nBest Quality Supplier:")
    print(result["best_quality_supplier"])

    print("\nLowest Defect Supplier:")
    print(result["lowest_defect_supplier"])
