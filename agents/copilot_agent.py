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


# =========================================================
# CONFIG
# =========================================================

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
# PROCUREMENT COPILOT
# =========================================================

def ask_procurement_copilot(
    question,
    supplier_scores,
    supplier_data,
    recommendation
):
    """
    Answers management questions using the current
    procurement analysis.
    """

    # -----------------------------------------------------
    # SUPPLIER DATA CONTEXT
    # -----------------------------------------------------

    relevant_columns = [
        "Supplier_ID",
        "Supplier_Name",
        "Cost_Efficiency_Score",
        "Overall_Quality_Score",
        "Overall_Risk_Score",
        "Overall_Procurement_Score"
    ]

    available_columns = [
        column
        for column in relevant_columns
        if column in supplier_scores.columns
    ]

    scores_context = supplier_scores[
        available_columns
    ].copy()

    scores_context = scores_context.to_string(
        index=False
    )

    # -----------------------------------------------------
    # ORIGINAL SUPPLIER DATA
    # -----------------------------------------------------

    supplier_columns = [
        "Supplier_ID",
        "Supplier_Name",
        "Unit_Price",
        "Quality_Score",
        "Defect_Rate",
        "Delivery_Reliability",
        "Lead_Time_Days",
        "Risk_Level",
        "Payment_Terms_Days",
        "Annual_Capacity",
        "Past_Performance_Score"
    ]

    available_supplier_columns = [
        column
        for column in supplier_columns
        if column in supplier_data.columns
    ]

    supplier_context = supplier_data[
        available_supplier_columns
    ].to_string(index=False)

    # -----------------------------------------------------
    # RECOMMENDATION
    # -----------------------------------------------------

    recommended_name = recommendation[
        "Supplier_Name"
    ]

    recommended_id = recommendation[
        "Supplier_ID"
    ]

    # =====================================================
    # PROMPT
    # =====================================================

    prompt = f"""
You are the Procurement Copilot for an enterprise
procurement decision-support system.

Answer the user's question using ONLY the supplier
information provided below.

Do not invent facts.
Do not introduce suppliers that are not present.
Do not claim causality that is not supported by the data.

CURRENT RECOMMENDATION

Supplier:
{recommended_name}

Supplier ID:
{recommended_id}

SUPPLIER SCORECARD

{scores_context}

SUPPLIER DATA

{supplier_context}

DECISION FRAMEWORK

Cost Weight: 40%
Quality Weight: 35%
Operational Risk Weight: 25%

USER QUESTION

{question}

INSTRUCTIONS

- Answer directly.
- Use the actual numbers when useful.
- Compare suppliers when the question asks for comparison.
- Explain the business reasoning clearly.
- Keep the response concise.
- If the data does not contain enough information to answer,
  explicitly say so.
"""

    # =====================================================
    # OLLAMA RESPONSE
    # =====================================================

    if OLLAMA_AVAILABLE:

        try:

            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response["message"]["content"]

        except Exception:

            pass

    # =====================================================
    # DETERMINISTIC FALLBACK
    # =====================================================

    return generate_fallback_response(
        question,
        supplier_scores,
        supplier_data,
        recommendation
    )


# =========================================================
# FALLBACK RESPONSE
# =========================================================

def generate_fallback_response(
    question,
    supplier_scores,
    supplier_data,
    recommendation
):
    """
    Simple rule-based fallback used when Ollama
    is unavailable.
    """

    question_lower = question.lower()

    recommended_name = recommendation[
        "Supplier_Name"
    ]

    recommended_id = recommendation[
        "Supplier_ID"
    ]

    # -----------------------------------------------------
    # WHY RECOMMENDED?
    # -----------------------------------------------------

    if (
        "why" in question_lower
        and (
            "recommend" in question_lower
            or "selected" in question_lower
            or "chosen" in question_lower
        )
    ):

        row = supplier_scores[
            supplier_scores["Supplier_ID"]
            == recommended_id
        ].iloc[0]

        return (
            f"{recommended_name} is recommended because it "
            f"achieved the highest overall procurement score "
            f"of {float(row['Overall_Procurement_Score']):.2f}. "
            f"Its Cost Efficiency Score is "
            f"{float(row['Cost_Efficiency_Score']):.2f}, "
            f"Quality Score is "
            f"{float(row['Overall_Quality_Score']):.2f}, "
            f"and Operational Risk Score is "
            f"{float(row['Overall_Risk_Score']):.2f}. "
            f"The model uses 40% Cost, 35% Quality and "
            f"25% Operational Risk."
        )

    # -----------------------------------------------------
    # CHEAPEST SUPPLIER
    # -----------------------------------------------------

    if (
        "cheapest" in question_lower
        or "lowest price" in question_lower
        or "lowest cost" in question_lower
    ):

        cheapest = supplier_data.loc[
            supplier_data["Unit_Price"].idxmin()
        ]

        return (
            f"The lowest-priced supplier is "
            f"{cheapest['Supplier_Name']} "
            f"({cheapest['Supplier_ID']}) at "
            f"₹{float(cheapest['Unit_Price']):.2f} per unit. "
            f"However, the procurement recommendation considers "
            f"cost together with quality and operational risk."
        )

    # -----------------------------------------------------
    # HIGHEST QUALITY
    # -----------------------------------------------------

    if (
        "highest quality" in question_lower
        or "best quality" in question_lower
        or "quality priority" in question_lower
    ):

        best_quality = supplier_scores.loc[
            supplier_scores[
                "Overall_Quality_Score"
            ].idxmax()
        ]

        return (
            f"{best_quality['Supplier_Name']} "
            f"({best_quality['Supplier_ID']}) has the highest "
            f"overall quality score of "
            f"{float(best_quality['Overall_Quality_Score']):.2f}."
        )

    # -----------------------------------------------------
    # LOWEST RISK
    # -----------------------------------------------------

    if (
        "lowest risk" in question_lower
        or "best risk" in question_lower
        or "risk priority" in question_lower
    ):

        best_risk = supplier_scores.loc[
            supplier_scores[
                "Overall_Risk_Score"
            ].idxmax()
        ]

        return (
            f"{best_risk['Supplier_Name']} "
            f"({best_risk['Supplier_ID']}) has the highest "
            f"Operational Risk Score of "
            f"{float(best_risk['Overall_Risk_Score']):.2f}, "
            f"which indicates the strongest operational resilience "
            f"among the evaluated suppliers."
        )

    # -----------------------------------------------------
    # COMPARE
    # -----------------------------------------------------

    if "compare" in question_lower:

        return (
            "I can compare suppliers using Cost Efficiency, "
            "Quality, Operational Risk and Overall Procurement Score. "
            "For a detailed comparison, ask a question such as: "
            "'Compare Vertex Industries and Delta Manufacturing.'"
        )

    # -----------------------------------------------------
    # DEFAULT
    # -----------------------------------------------------

    return (
        f"The current procurement recommendation is "
        f"{recommended_name} ({recommended_id}). "
        f"The decision is based on Cost, Quality and Operational "
        f"Risk using weights of 40%, 35% and 25% respectively. "
        f"For a more specific answer, ask about a supplier, "
        f"cost, quality, risk or comparison."
    )
