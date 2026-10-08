import pandas as pd
import numpy as np


def analyze_cost(df):
    """
    Analyze suppliers based on:
    - Unit Price
    - Payment Terms
    - Overall cost efficiency
    """

    data = df.copy()

    # Lowest unit price
    min_price = data["Unit_Price"].min()
    max_price = data["Unit_Price"].max()

    # Cost score: lower price = higher score
    if max_price == min_price:
        data["Cost_Score"] = 100
    else:
        data["Cost_Score"] = (
            (max_price - data["Unit_Price"])
            / (max_price - min_price)
        ) * 100

    # Payment terms score
    min_payment = data["Payment_Terms_Days"].min()
    max_payment = data["Payment_Terms_Days"].max()

    if max_payment == min_payment:
        data["Payment_Score"] = 100
    else:
        data["Payment_Score"] = (
            (data["Payment_Terms_Days"] - min_payment)
            / (max_payment - min_payment)
        ) * 100

    # Combined cost efficiency
    data["Cost_Efficiency_Score"] = (
        data["Cost_Score"] * 0.75
        + data["Payment_Score"] * 0.25
    )

    # Rank suppliers
    data["Cost_Rank"] = (
        data["Cost_Efficiency_Score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    # Best supplier from cost perspective
    best_supplier = data.loc[
        data["Cost_Efficiency_Score"].idxmax()
    ]

    # Lowest price supplier
    lowest_price_supplier = data.loc[
        data["Unit_Price"].idxmin()
    ]

    result = {
        "supplier_analysis": data[
            [
                "Supplier_ID",
                "Supplier_Name",
                "Unit_Price",
                "Payment_Terms_Days",
                "Cost_Score",
                "Payment_Score",
                "Cost_Efficiency_Score",
                "Cost_Rank"
            ]
        ].sort_values("Cost_Rank"),

        "best_cost_supplier": {
            "Supplier_ID": best_supplier["Supplier_ID"],
            "Supplier_Name": best_supplier["Supplier_Name"],
            "Unit_Price": best_supplier["Unit_Price"],
            "Cost_Efficiency_Score": round(
                best_supplier["Cost_Efficiency_Score"], 2
            )
        },

        "lowest_price_supplier": {
            "Supplier_ID": lowest_price_supplier["Supplier_ID"],
            "Supplier_Name": lowest_price_supplier["Supplier_Name"],
            "Unit_Price": lowest_price_supplier["Unit_Price"]
        }
    }

    return result


if __name__ == "__main__":

    df = pd.read_csv("data/supplier_data.csv")

    result = analyze_cost(df)

    print("\n===== COST ANALYSIS =====\n")

    print(
        result["supplier_analysis"].to_string(index=False)
    )

    print("\nBest Cost Supplier:")
    print(result["best_cost_supplier"])

    print("\nLowest Price Supplier:")
    print(result["lowest_price_supplier"])
