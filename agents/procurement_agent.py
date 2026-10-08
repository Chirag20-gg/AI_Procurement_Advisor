import os
import sys
import pandas as pd

# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import OLLAMA_MODEL

# =========================================================
# OLLAMA
# =========================================================

try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    ollama = None
    OLLAMA_AVAILABLE = False


# =========================================================
# HELPERS
# =========================================================

def _extract_dataframe(result):
    """Extract a DataFrame from an agent result."""

    if isinstance(result, pd.DataFrame):
        return result.copy()

    if isinstance(result, dict):
        # Most likely key first
        for key in ["supplier_scores", "ranking", "data", "result", "analysis", "df", "table"]:
            value = result.get(key)
            if isinstance(value, pd.DataFrame):
                return value.copy()

        # Search nested values
        for value in result.values():
            if isinstance(value, pd.DataFrame):
                return value.copy()
            if isinstance(value, list) and value and isinstance(value[0], dict):
                return pd.DataFrame(value)

    if isinstance(result, list) and result and isinstance(result[0], dict):
        return pd.DataFrame(result)

    raise TypeError("Could not find supplier data in the agent result.")


def _find_column(df, names):
    for name in names:
        if name in df.columns:
            return name
    return None


# =========================================================
# PREPARE COST DATA
# =========================================================

def _prepare_cost_data(result):
    df = _extract_dataframe(result)

    sid = _find_column(df, ["Supplier_ID", "supplier_id", "Supplier ID"])
    name = _find_column(df, ["Supplier_Name", "supplier_name", "Supplier Name"])
    price = _find_column(df, ["Unit_Price", "unit_price", "Unit Price"])
    score = _find_column(df, [
        "Cost_Efficiency_Score",
        "Cost Score",
        "Cost_Score",
        "cost_score"
    ])

    required = {
        "Supplier_ID": sid,
        "Supplier_Name": name,
        "Unit_Price": price,
        "Cost_Efficiency_Score": score
    }

    missing = [key for key, value in required.items() if value is None]
    if missing:
        raise KeyError(f"Missing Cost Agent columns: {', '.join(missing)}")

    out = df[[sid, name, price, score]].copy()
    out.columns = [
        "Supplier_ID",
        "Supplier_Name",
        "Unit_Price",
        "Cost_Efficiency_Score"
    ]
    return out


# =========================================================
# PREPARE QUALITY DATA
# =========================================================

def _prepare_quality_data(result):
    df = _extract_dataframe(result)

    sid = _find_column(df, ["Supplier_ID", "supplier_id", "Supplier ID"])
    quality = _find_column(df, ["Quality_Score", "quality_score", "Quality Score"])
    defect = _find_column(df, ["Defect_Rate", "defect_rate", "Defect Rate"])
    overall = _find_column(df, [
        "Overall_Quality_Score",
        "Quality_Score_Overall",
        "Overall Quality Score",
        "Overall_Quality"
    ])

    required = {
        "Supplier_ID": sid,
        "Quality_Score": quality,
        "Defect_Rate": defect,
        "Overall_Quality_Score": overall
    }

    missing = [key for key, value in required.items() if value is None]
    if missing:
        raise KeyError(f"Missing Quality Agent columns: {', '.join(missing)}")

    out = df[[sid, quality, defect, overall]].copy()
    out.columns = [
        "Supplier_ID",
        "Quality_Score",
        "Defect_Rate",
        "Overall_Quality_Score"
    ]
    return out


# =========================================================
# PREPARE RISK DATA
# =========================================================

def _prepare_risk_data(result):
    df = _extract_dataframe(result)

    sid = _find_column(df, ["Supplier_ID", "supplier_id", "Supplier ID"])
    risk_level = _find_column(df, ["Risk_Level", "Risk Level", "risk_level"])
    delivery = _find_column(df, [
        "Delivery_Reliability",
        "Delivery Reliability",
        "delivery_reliability"
    ])
    lead = _find_column(df, [
        "Lead_Time_Days",
        "Lead Time",
        "Lead_Time",
        "lead_time_days"
    ])
    risk_score = _find_column(df, [
        # This is the name your existing app expects
        "Overall_Risk_Score",
        "Overall Risk Score",
        "Operational_Risk_Score",
        "Operational Risk Score",
        "Risk_Score",
        "Risk Score",
        "Overall_Risk"
    ])

    if sid is None:
        raise KeyError("Supplier_ID not found in Risk Agent output.")

    out = pd.DataFrame()
    out["Supplier_ID"] = df[sid]

    if risk_level is not None:
        out["Risk_Level"] = df[risk_level]
    else:
        out["Risk_Level"] = "Unknown"

    if delivery is not None:
        out["Delivery_Reliability"] = pd.to_numeric(df[delivery], errors="coerce")
    else:
        out["Delivery_Reliability"] = 0

    if lead is not None:
        out["Lead_Time_Days"] = pd.to_numeric(df[lead], errors="coerce")
    else:
        out["Lead_Time_Days"] = 0

    # If the Risk Agent already calculated the score, preserve it.
    if risk_score is not None:
        out["Overall_Risk_Score"] = pd.to_numeric(
            df[risk_score], errors="coerce"
        )
    else:
        # Fallback calculation only if necessary.
        risk_mapping = {
            "Low": 100,
            "Medium": 60,
            "High": 20
        }

        level_score = out["Risk_Level"].map(risk_mapping).fillna(50)
        delivery_score = out["Delivery_Reliability"].fillna(0).clip(0, 100)

        lead_values = out["Lead_Time_Days"].fillna(0)
        max_lead = lead_values.max()
        min_lead = lead_values.min()

        if max_lead > 0 and max_lead != min_lead:
            lead_score = (
                (max_lead - lead_values) /
                (max_lead - min_lead) * 100
            )
        else:
            lead_score = pd.Series(100, index=out.index)

        out["Overall_Risk_Score"] = (
            level_score * 0.40
            + delivery_score * 0.30
            + lead_score * 0.30
        )

    return out


# =========================================================
# AI STRATEGY
# =========================================================

def _generate_strategy(recommended, backup):
    prompt = f"""
You are a procurement strategy expert.

Based only on the information below, explain the procurement recommendation.

Recommended Supplier: {recommended['Supplier_Name']} ({recommended['Supplier_ID']})
Overall Procurement Score: {recommended['Overall_Procurement_Score']:.2f}
Cost Efficiency Score: {recommended['Cost_Efficiency_Score']:.2f}
Quality Score: {recommended['Overall_Quality_Score']:.2f}
Operational Risk Score: {recommended['Overall_Risk_Score']:.2f}
Risk Level: {recommended['Risk_Level']}
Unit Price: ₹{recommended['Unit_Price']:.2f}

Backup Supplier: {backup['Supplier_Name'] if backup is not None else 'Not available'}

Give:
1. Why the recommended supplier was selected.
2. Main strengths.
3. One potential concern.
4. Why the backup supplier is relevant.

Do not invent facts. Keep it concise and management-oriented.
"""

    if OLLAMA_AVAILABLE:
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        except Exception:
            pass

    text = (
        f"{recommended['Supplier_Name']} is the recommended supplier with an "
        f"overall procurement score of {recommended['Overall_Procurement_Score']:.2f}. "
        f"The recommendation combines cost efficiency, quality and operational resilience. "
        f"The supplier has a {recommended['Risk_Level']} risk level and a unit price of "
        f"₹{recommended['Unit_Price']:.2f}."
    )

    if backup is not None:
        text += f" {backup['Supplier_Name']} is the backup supplier based on the overall ranking."

    return text


# =========================================================
# MAIN PROCUREMENT ANALYSIS
# =========================================================

def analyze_procurement(cost_result, quality_result, risk_result):
    """
    Combines the three existing agent outputs.

    IMPORTANT:
    The return structure intentionally matches the existing app.py:
      - supplier_scores
      - recommended_supplier
      - strategy
    """

    cost_df = _prepare_cost_data(cost_result)
    quality_df = _prepare_quality_data(quality_result)
    risk_df = _prepare_risk_data(risk_result)

    supplier_scores = cost_df.merge(
        quality_df,
        on="Supplier_ID",
        how="inner"
    ).merge(
        risk_df,
        on="Supplier_ID",
        how="inner"
    )

    # Default procurement weighting used by the current dashboard.
    supplier_scores["Overall_Procurement_Score"] = (
        supplier_scores["Cost_Efficiency_Score"] * 0.40
        + supplier_scores["Overall_Quality_Score"] * 0.35
        + supplier_scores["Overall_Risk_Score"] * 0.25
    )

    supplier_scores = supplier_scores.sort_values(
        "Overall_Procurement_Score",
        ascending=False
    ).reset_index(drop=True)

    supplier_scores["Procurement_Rank"] = supplier_scores.index + 1

    # Recommendation must be a dictionary because app.py uses
    # recommendation['Supplier_Name'], etc.
    recommendation = supplier_scores.iloc[0].to_dict()

    backup = (
        supplier_scores.iloc[1].to_dict()
        if len(supplier_scores) > 1
        else None
    )

    strategy = _generate_strategy(
        supplier_scores.iloc[0],
        supplier_scores.iloc[1] if len(supplier_scores) > 1 else None
    )

    return {
        "supplier_scores": supplier_scores,
        "recommended_supplier": recommendation,
        "strategy": strategy,
        # Extra fields are harmless and useful for later features.
        "backup_supplier": (
            backup["Supplier_Name"] if backup is not None else None
        )
    }


# =========================================================
# WHAT-IF PROCUREMENT SIMULATOR
# =========================================================

def calculate_custom_procurement_scores(
    cost_result,
    quality_result,
    risk_result,
    cost_weight,
    quality_weight,
    risk_weight
):
    """Recalculate rankings using custom Cost/Quality/Risk weights."""

    total = cost_weight + quality_weight + risk_weight

    if total != 100:
        raise ValueError("Cost, Quality and Risk weights must add up to 100%.")

    cost_df = _prepare_cost_data(cost_result)
    quality_df = _prepare_quality_data(quality_result)
    risk_df = _prepare_risk_data(risk_result)

    scores = cost_df.merge(
        quality_df,
        on="Supplier_ID",
        how="inner"
    ).merge(
        risk_df,
        on="Supplier_ID",
        how="inner"
    )

    scores["Custom_Procurement_Score"] = (
        scores["Cost_Efficiency_Score"] * (cost_weight / 100)
        + scores["Overall_Quality_Score"] * (quality_weight / 100)
        + scores["Overall_Risk_Score"] * (risk_weight / 100)
    )

    scores = scores.sort_values(
        "Custom_Procurement_Score",
        ascending=False
    ).reset_index(drop=True)

    scores["Rank"] = scores.index + 1

    return scores
