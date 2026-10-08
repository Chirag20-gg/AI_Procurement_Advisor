import streamlit as st
import pandas as pd
import plotly.express as px

from agents.orchestrator import run_procurement_analysis
from agents.copilot_agent import ask_procurement_copilot


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Procurement Advisor",
    page_icon="📦",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("📦 AI Procurement Advisor")

st.markdown(
    """
    ### Domain-Expert Multi-Agent System for Supplier Selection

    This application evaluates suppliers across **Cost, Quality,
    and Operational Risk** and provides an AI-powered procurement
    recommendation.
    """
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Analysis Settings")

analysis_mode = st.sidebar.radio(
    "Select Dataset",
    [
        "Demo Dataset",
        "Upload Dataset"
    ]
)


# =========================================================
# LOAD DATA
# =========================================================

if analysis_mode == "Demo Dataset":

    df = pd.read_csv(
        "data/supplier_data.csv"
    )

else:

    uploaded_file = st.sidebar.file_uploader(
        "Upload Supplier CSV",
        type=["csv"]
    )

    if uploaded_file is None:

        st.info(
            "Please upload a supplier CSV file from the sidebar."
        )

        st.stop()

    df = pd.read_csv(uploaded_file)


# =========================================================
# DATA VALIDATION
# =========================================================

required_columns = [
    "Supplier_ID",
    "Supplier_Name",
    "Category",
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

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "The uploaded dataset is missing: "
        + ", ".join(missing_columns)
    )

    st.stop()


# =========================================================
# DATASET OVERVIEW
# =========================================================

st.subheader("📊 Supplier Dataset")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Suppliers",
        len(df)
    )

with col2:

    st.metric(
        "Average Unit Price",
        f"₹{df['Unit_Price'].mean():.2f}"
    )

with col3:

    st.metric(
        "Average Quality",
        f"{df['Quality_Score'].mean():.1f}"
    )

with col4:

    st.metric(
        "Low Risk Suppliers",
        len(
            df[
                df["Risk_Level"].str.lower() == "low"
            ]
        )
    )


with st.expander("View Supplier Data"):

    st.dataframe(
        df,
        use_container_width=True
    )


# =========================================================
# ARCHITECTURE
# =========================================================

st.subheader("🤖 Multi-Agent Architecture")

st.info(
    """
    **User → Orchestrator → Cost Agent + Quality Agent + Risk Agent
    → Procurement Strategist → Final Recommendation**
    """
)


# =========================================================
# ANALYSIS BUTTON
# =========================================================

st.subheader("🔍 Procurement Analysis")

run_analysis = st.button(
    "🚀 Run AI Procurement Analysis",
    use_container_width=True
)


# =========================================================
# RUN ANALYSIS
# =========================================================

if run_analysis:

    with st.spinner(
        "AI agents are analyzing suppliers..."
    ):

        result = run_procurement_analysis(df)

    st.session_state["procurement_result"] = result


# =========================================================
# DISPLAY RESULTS
# =========================================================

if "procurement_result" in st.session_state:

    result = st.session_state["procurement_result"]

    # =====================================================
    # EXTRACT RESULTS
    # =====================================================

    cost_result = result["cost_analysis"]

    quality_result = result["quality_analysis"]

    risk_result = result["risk_analysis"]

    procurement_result = result["procurement_analysis"]

    supplier_scores = procurement_result[
        "supplier_scores"
    ]

    recommendation = procurement_result[
        "recommended_supplier"
    ]

    strategy = procurement_result[
        "strategy"
    ]


    # =====================================================
    # RECOMMENDATION
    # =====================================================

    st.success(
        f"Recommended Supplier: "
        f"**{recommendation['Supplier_Name']} "
        f"({recommendation['Supplier_ID']})**"
    )


    # =====================================================
    # RECOMMENDATION OVERVIEW
    # =====================================================

    st.subheader("🏆 Recommendation Overview")

    c1, c2, c3, c4 = st.columns(4)

    recommended_id = recommendation[
        "Supplier_ID"
    ]

    recommended_row = df[
        df["Supplier_ID"] == recommended_id
    ].iloc[0]

    with c1:

        st.metric(
            "Recommended Supplier",
            recommendation["Supplier_Name"]
        )

    with c2:

        st.metric(
            "Procurement Score",
            f"{float(recommendation['Overall_Procurement_Score']):.2f}"
        )

    with c3:

        st.metric(
            "Unit Price",
            f"₹{int(recommended_row['Unit_Price'])}"
        )

    with c4:

        st.metric(
            "Risk Level",
            str(recommended_row["Risk_Level"])
        )


    # =====================================================
    # SUPPLIER SCORE COMPARISON
    # =====================================================

    st.subheader("📈 Supplier Score Comparison")

    chart_data = supplier_scores[
        [
            "Supplier_Name",
            "Cost_Efficiency_Score",
            "Overall_Quality_Score",
            "Overall_Risk_Score",
            "Overall_Procurement_Score"
        ]
    ].copy()

    chart_data = chart_data.melt(
        id_vars="Supplier_Name",
        var_name="Score Type",
        value_name="Score"
    )

    fig = px.bar(
        chart_data,
        x="Supplier_Name",
        y="Score",
        color="Score Type",
        barmode="group",
        title="Supplier Performance Across Decision Dimensions"
    )

    fig.update_layout(
        xaxis_title="Supplier",
        yaxis_title="Score",
        legend_title="Metric"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # =====================================================
    # FINAL RANKING
    # =====================================================

    st.subheader("🥇 Final Supplier Ranking")

    ranking_display = supplier_scores[
        [
            "Procurement_Rank",
            "Supplier_ID",
            "Supplier_Name",
            "Cost_Efficiency_Score",
            "Overall_Quality_Score",
            "Overall_Risk_Score",
            "Overall_Procurement_Score"
        ]
    ].copy()

    ranking_display.columns = [
        "Rank",
        "Supplier ID",
        "Supplier Name",
        "Cost Score",
        "Quality Score",
        "Operational Risk Score",
        "Overall Procurement Score"
    ]

    st.dataframe(
        ranking_display,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # WHAT-IF PROCUREMENT SIMULATOR
    # =====================================================

    st.divider()

    st.subheader("🔄 What-If Procurement Simulator")

    st.markdown(
        """
        Test how the supplier recommendation changes when management
        changes its priorities between **Cost, Quality and Operational Risk**.
        """
    )

    scenario = st.selectbox(
        "Select Procurement Scenario",
        [
            "Balanced",
            "Cost Focused",
            "Quality Focused",
            "Risk Focused",
            "Custom"
        ]
    )

    scenario_weights = {

        "Balanced": {
            "cost": 40,
            "quality": 35,
            "risk": 25
        },

        "Cost Focused": {
            "cost": 60,
            "quality": 25,
            "risk": 15
        },

        "Quality Focused": {
            "cost": 25,
            "quality": 50,
            "risk": 25
        },

        "Risk Focused": {
            "cost": 25,
            "quality": 25,
            "risk": 50
        }
    }

    if scenario == "Custom":

        w1, w2, w3 = st.columns(3)

        with w1:

            cost_weight = st.slider(
                "Cost Weight",
                0,
                100,
                40,
                5
            )

        with w2:

            quality_weight = st.slider(
                "Quality Weight",
                0,
                100,
                35,
                5
            )

        with w3:

            risk_weight = st.slider(
                "Operational Risk Weight",
                0,
                100,
                25,
                5
            )

    else:

        cost_weight = scenario_weights[
            scenario
        ]["cost"]

        quality_weight = scenario_weights[
            scenario
        ]["quality"]

        risk_weight = scenario_weights[
            scenario
        ]["risk"]

    total_weight = (
        cost_weight
        + quality_weight
        + risk_weight
    )

    wc1, wc2, wc3, wc4 = st.columns(4)

    with wc1:
        st.metric("Cost", f"{cost_weight}%")

    with wc2:
        st.metric("Quality", f"{quality_weight}%")

    with wc3:
        st.metric(
            "Operational Risk",
            f"{risk_weight}%"
        )

    with wc4:
        st.metric(
            "Total",
            f"{total_weight}%"
        )

    if total_weight != 100:

        st.warning(
            "The three weights must add up to 100%."
        )

    else:

        scenario_scores = supplier_scores[
            [
                "Supplier_ID",
                "Supplier_Name",
                "Cost_Efficiency_Score",
                "Overall_Quality_Score",
                "Overall_Risk_Score"
            ]
        ].copy()

        scenario_scores[
            "Scenario_Procurement_Score"
        ] = (

            scenario_scores[
                "Cost_Efficiency_Score"
            ] * (cost_weight / 100)

            +

            scenario_scores[
                "Overall_Quality_Score"
            ] * (quality_weight / 100)

            +

            scenario_scores[
                "Overall_Risk_Score"
            ] * (risk_weight / 100)
        )

        scenario_scores = scenario_scores.sort_values(
            "Scenario_Procurement_Score",
            ascending=False
        ).reset_index(drop=True)

        scenario_scores[
            "Scenario_Rank"
        ] = scenario_scores.index + 1

        scenario_winner = scenario_scores.iloc[0]

        st.markdown("### 🎯 Scenario Recommendation")

        st.success(
            f"Under the **{scenario}** scenario, "
            f"the recommended supplier is "
            f"**{scenario_winner['Supplier_Name']} "
            f"({scenario_winner['Supplier_ID']})**."
        )

        sc1, sc2, sc3 = st.columns(3)

        with sc1:

            st.metric(
                "Recommended Supplier",
                scenario_winner["Supplier_Name"]
            )

        with sc2:

            st.metric(
                "Scenario Score",
                f"{float(scenario_winner['Scenario_Procurement_Score']):.2f}"
            )

        with sc3:

            winner_original_rank = supplier_scores[
                supplier_scores["Supplier_ID"]
                == scenario_winner["Supplier_ID"]
            ]["Procurement_Rank"].iloc[0]

            st.metric(
                "Original Rank",
                int(winner_original_rank)
            )

        if (
            recommendation["Supplier_ID"]
            == scenario_winner["Supplier_ID"]
        ):

            st.info(
                "The recommended supplier remains the same "
                "under this scenario."
            )

        else:

            st.warning(
                f"The recommendation changes from "
                f"**{recommendation['Supplier_Name']}** "
                f"to **{scenario_winner['Supplier_Name']}** "
                f"under this scenario."
            )

        st.markdown(
            "### 📊 Scenario Supplier Ranking"
        )

        scenario_display = scenario_scores[
            [
                "Scenario_Rank",
                "Supplier_ID",
                "Supplier_Name",
                "Cost_Efficiency_Score",
                "Overall_Quality_Score",
                "Overall_Risk_Score",
                "Scenario_Procurement_Score"
            ]
        ].copy()

        scenario_display.columns = [
            "Rank",
            "Supplier ID",
            "Supplier Name",
            "Cost Score",
            "Quality Score",
            "Operational Risk Score",
            "Scenario Score"
        ]

        st.dataframe(
            scenario_display,
            use_container_width=True,
            hide_index=True
        )


    # =====================================================
    # DOMAIN EXPERT INSIGHTS
    # =====================================================

    st.subheader("🧠 Domain Expert Insights")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "💰 Cost Agent",
            "⭐ Quality Agent",
            "⚠️ Risk Agent",
            "🎯 Procurement Strategist"
        ]
    )


    # -----------------------------------------------------
    # COST AGENT
    # -----------------------------------------------------

    with tab1:

        cost_supplier = cost_result[
            "best_cost_supplier"
        ]

        st.write(
            "Best supplier from a cost perspective:"
        )

        st.success(
            cost_supplier["Supplier_Name"]
        )

        st.markdown(
            f"""
            **Supplier ID:** {cost_supplier['Supplier_ID']}

            **Unit Price:** ₹{int(cost_supplier['Unit_Price'])}

            **Cost Efficiency Score:** {float(cost_supplier['Cost_Efficiency_Score']):.2f}
            """
        )


    # -----------------------------------------------------
    # QUALITY AGENT
    # -----------------------------------------------------

    with tab2:

        quality_supplier = quality_result[
            "best_quality_supplier"
        ]

        st.write(
            "Best supplier from a quality perspective:"
        )

        st.success(
            quality_supplier["Supplier_Name"]
        )

        st.markdown(
            f"""
            **Supplier ID:** {quality_supplier['Supplier_ID']}

            **Quality Score:** {int(quality_supplier['Quality_Score'])}

            **Defect Rate:** {float(quality_supplier['Defect_Rate']):.1f}%

            **Overall Quality Score:** {float(quality_supplier['Overall_Quality_Score']):.2f}
            """
        )


    # -----------------------------------------------------
    # RISK AGENT
    # -----------------------------------------------------

    with tab3:

        risk_supplier = risk_result[
            "best_risk_supplier"
        ]

        st.write(
            "Best supplier from an operational risk perspective:"
        )

        st.success(
            risk_supplier["Supplier_Name"]
        )

        st.markdown(
            f"""
            **Supplier ID:** {risk_supplier['Supplier_ID']}

            **Risk Level:** {risk_supplier['Risk_Level']}

            **Delivery Reliability:** {int(risk_supplier['Delivery_Reliability'])}%

            **Lead Time:** {int(risk_supplier['Lead_Time_Days'])} days

            **Operational Risk Score:** {float(risk_supplier['Overall_Risk_Score']):.2f}

            *Higher Operational Risk Score indicates stronger operational resilience.*
            """
        )


    # -----------------------------------------------------
    # PROCUREMENT STRATEGIST
    # -----------------------------------------------------

    with tab4:

        st.markdown(strategy)


    # =====================================================
    # PROCUREMENT COPILOT
    # =====================================================

    st.divider()

    st.subheader("🤖 Procurement Copilot")

    st.markdown(
        """
        Ask questions about the current supplier analysis.
        
        Examples:
        - Why was this supplier recommended?
        - Why wasn't Gamma Traders selected despite being cheapest?
        - Which supplier has the best quality?
        - Which supplier has the lowest operational risk?
        - Compare two suppliers.
        """
    )

    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------

    if "copilot_messages" not in st.session_state:

        st.session_state["copilot_messages"] = []


    # -----------------------------------------------------
    # DISPLAY CHAT HISTORY
    # -----------------------------------------------------

    for message in st.session_state[
        "copilot_messages"
    ]:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------

    user_question = st.chat_input(
        "Ask the Procurement Copilot..."
    )


    if user_question:

        # ---------------------------------------------
        # USER MESSAGE
        # ---------------------------------------------

        st.session_state[
            "copilot_messages"
        ].append(
            {
                "role": "user",
                "content": user_question
            }
        )

        with st.chat_message("user"):

            st.markdown(
                user_question
            )


        # ---------------------------------------------
        # AI RESPONSE
        # ---------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "Procurement Copilot is analyzing..."
            ):

                answer = ask_procurement_copilot(
                    user_question,
                    supplier_scores,
                    df,
                    recommendation
                )

            st.markdown(answer)


        # ---------------------------------------------
        # SAVE RESPONSE
        # ---------------------------------------------

        st.session_state[
            "copilot_messages"
        ].append(
            {
                "role": "assistant",
                "content": answer
            }
        )


    # =====================================================
    # WHY THIS SUPPLIER?
    # =====================================================

    st.subheader("⚖️ Why This Supplier?")

    st.markdown(
        f"""
        The system does not select a supplier based on price alone.

        The final recommendation considers:

        - **40% Cost Efficiency**
        - **35% Quality**
        - **25% Operational Risk**

        **{recommendation['Supplier_Name']}** achieved the
        highest combined procurement score of
        **{float(recommendation['Overall_Procurement_Score']):.2f}**.
        """
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "AI Procurement Advisor | "
    "Domain-Expert Multi-Agent System"
)