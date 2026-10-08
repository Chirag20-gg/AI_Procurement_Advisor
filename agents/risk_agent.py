import pandas as pd


def analyze_risk(df):
    """
    Analyze suppliers based on:
    - Risk Level
    - Delivery Reliability
    - Lead Time
    - Annual Capacity
    """

    data = df.copy()

    # Convert Risk Level into a numerical score
    # Lower risk = better
    risk_mapping = {
        "Low": 100,
        "Medium": 60,
        "High": 20
    }

    data["Risk_Level_Score"] = (
        data["Risk_Level"]
        .map(risk_mapping)
        .fillna(50)
    )

    # Delivery reliability:
    # Higher reliability = better
    data["Delivery_Score"] = data["Delivery_Reliability"]

    # Lead time:
    # Lower lead time = better
    lead_min = data["Lead_Time_Days"].min()
    lead_max = data["Lead_Time_Days"].max()

    if lead_max == lead_min:
        data["Lead_Time_Score"] = 100
    else:
        data["Lead_Time_Score"] = (
            (lead_max - data["Lead_Time_Days"])
            / (lead_max - lead_min)
        ) * 100

    # Annual capacity:
    # Higher capacity = better
    capacity_min = data["Annual_Capacity"].min()
    capacity_max = data["Annual_Capacity"].max()

    if capacity_max == capacity_min:
        data["Capacity_Score"] = 100
    else:
        data["Capacity_Score"] = (
            (data["Annual_Capacity"] - capacity_min)
            / (capacity_max - capacity_min)
        ) * 100

    # Overall Risk Score
    data["Overall_Risk_Score"] = (
        data["Risk_Level_Score"] * 0.40
        + data["Delivery_Score"] * 0.30
        + data["Lead_Time_Score"] * 0.20
        + data["Capacity_Score"] * 0.10
    )

    # Rank suppliers
    data["Risk_Rank"] = (
        data["Overall_Risk_Score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    # Best supplier from risk perspective
    best_supplier = data.loc[
        data["Overall_Risk_Score"].idxmax()
    ]

    # Highest delivery reliability
    best_delivery_supplier = data.loc[
        data["Delivery_Reliability"].idxmax()
    ]

    # Lowest risk suppliers
    low_risk_suppliers = data[
        data["Risk_Level"] == "Low"
    ].copy()

    result = {
        "supplier_analysis": data[
            [
                "Supplier_ID",
                "Supplier_Name",
                "Risk_Level",
                "Delivery_Reliability",
                "Lead_Time_Days",
                "Annual_Capacity",
                "Risk_Level_Score",
                "Delivery_Score",
                "Lead_Time_Score",
                "Capacity_Score",
                "Overall_Risk_Score",
                "Risk_Rank"
            ]
        ].sort_values("Risk_Rank"),

        "best_risk_supplier": {
            "Supplier_ID": best_supplier["Supplier_ID"],
            "Supplier_Name": best_supplier["Supplier_Name"],
            "Risk_Level": best_supplier["Risk_Level"],
            "Delivery_Reliability": best_supplier["Delivery_Reliability"],
            "Lead_Time_Days": best_supplier["Lead_Time_Days"],
            "Overall_Risk_Score": round(
                best_supplier["Overall_Risk_Score"], 2
            )
        },

        "best_delivery_supplier": {
            "Supplier_ID": best_delivery_supplier["Supplier_ID"],
            "Supplier_Name": best_delivery_supplier["Supplier_Name"],
            "Delivery_Reliability": best_delivery_supplier[
                "Delivery_Reliability"
            ]
        },

        "low_risk_suppliers": low_risk_suppliers[
            [
                "Supplier_ID",
                "Supplier_Name",
                "Risk_Level",
                "Delivery_Reliability",
                "Lead_Time_Days"
            ]
        ].to_dict("records")
    }

    return result


if __name__ == "__main__":

    df = pd.read_csv("data/supplier_data.csv")

    result = analyze_risk(df)

    print("\n===== RISK ANALYSIS =====\n")

    print(
        result["supplier_analysis"].to_string(index=False)
    )

    print("\nBest Risk Supplier:")
    print(result["best_risk_supplier"])

    print("\nBest Delivery Supplier:")
    print(result["best_delivery_supplier"])

    print("\nLow Risk Suppliers:")
    for supplier in result["low_risk_suppliers"]:
        print(supplier)
