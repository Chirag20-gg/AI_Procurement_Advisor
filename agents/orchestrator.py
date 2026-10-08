import os
import sys
import pandas as pd

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from agents.cost_agent import analyze_cost
from agents.quality_agent import analyze_quality
from agents.risk_agent import analyze_risk
from agents.procurement_agent import analyze_procurement


def run_procurement_analysis(df):
    """
    Run the complete multi-agent procurement workflow.

    Workflow:
    1. Cost Agent
    2. Quality Agent
    3. Risk Agent
    4. Procurement Strategist
    """

    # Step 1: Cost Analysis
    cost_result = analyze_cost(df)

    # Step 2: Quality Analysis
    quality_result = analyze_quality(df)

    # Step 3: Risk Analysis
    risk_result = analyze_risk(df)

    # Step 4: Final Procurement Strategy
    procurement_result = analyze_procurement(
        cost_result,
        quality_result,
        risk_result
    )

    return {
        "cost_analysis": cost_result,
        "quality_analysis": quality_result,
        "risk_analysis": risk_result,
        "procurement_analysis": procurement_result
    }


if __name__ == "__main__":

    # Load supplier data
    df = pd.read_csv(
        "data/supplier_data.csv"
    )

    # Run complete workflow
    result = run_procurement_analysis(df)

    print("\n")
    print("=" * 60)
    print("       AI PROCUREMENT ADVISOR")
    print("       MULTI-AGENT ANALYSIS")
    print("=" * 60)

    print("\nCOST AGENT")
    print("-" * 60)

    print(
        result["cost_analysis"]["best_cost_supplier"]
    )

    print("\nQUALITY AGENT")
    print("-" * 60)

    print(
        result["quality_analysis"]["best_quality_supplier"]
    )

    print("\nRISK AGENT")
    print("-" * 60)

    print(
        result["risk_analysis"]["best_risk_supplier"]
    )

    print("\nFINAL PROCUREMENT DECISION")
    print("-" * 60)

    print(
        result["procurement_analysis"][
            "recommended_supplier"
        ]
    )

    print("\nPROCUREMENT STRATEGY")
    print("-" * 60)

    print(
        result["procurement_analysis"]["strategy"]
    )

    print("\n")
    print("=" * 60)
    print("             ANALYSIS COMPLETE")
    print("=" * 60)
