
# AI Procurement Advisor

A domain-expert multi-agent AI system for supplier selection and procurement decision support.

## Overview

AI Procurement Advisor helps procurement managers evaluate and compare suppliers using three major dimensions:

- Cost
- Quality
- Operational Risk

Instead of selecting a supplier only based on price, the system combines multiple supplier factors and generates a transparent overall procurement recommendation.

The application also includes a What-If Simulator for testing different procurement priorities and a Procurement Copilot for asking questions about supplier performance in natural language.

## Business Problem

Supplier selection often involves multiple factors such as price, quality, delivery reliability, lead time and supplier risk.

A supplier with the lowest price may not always be the best choice if it has poor quality or high operational risk.

This project provides a structured way to:

1. Analyse supplier information
2. Evaluate cost, quality and risk separately
3. Combine the results into an overall procurement score
4. Rank suppliers
5. Recommend the most suitable supplier
6. Test different procurement priorities
7. Ask natural-language questions about the analysis

## System Architecture

```text
User
  ↓
Streamlit Application
  ↓
Orchestrator
  ↓
┌───────────────┬────────────────┬────────────────┐
│   Cost Agent  │ Quality Agent  │   Risk Agent   │
└───────────────┴────────────────┴────────────────┘
                  ↓
        Procurement Strategist
                  ↓
       Supplier Recommendation
                  ↓
      ┌────────────────────────┐
      │    What-If Simulator   │
      │    Procurement Copilot │
      └────────────────────────┘
```

## Agents

### 1. Cost Agent

Evaluates suppliers based on:

- Unit price
- Payment terms

The Cost Agent produces a Cost Efficiency Score.

### 2. Quality Agent

Evaluates:

- Quality score
- Defect rate
- Past performance

The Quality Agent produces an Overall Quality Score.

### 3. Risk Agent

Evaluates:

- Supplier risk level
- Delivery reliability
- Lead time
- Annual capacity

The Risk Agent produces an Operational Risk Score.

### 4. Procurement Strategist

Combines the outputs from the Cost, Quality and Risk Agents and generates the final supplier ranking and recommendation.

### 5. Orchestrator

Coordinates the complete workflow and ensures that the different agents run in the correct sequence.

### 6. Procurement Copilot

Provides a natural-language interface for asking questions about the current supplier analysis.

Example questions:

- Why was this supplier recommended?
- Which supplier is the cheapest?
- Which supplier has the highest quality?
- Which supplier has the lowest risk?
- Compare two suppliers.

## Procurement Scoring

The default procurement model uses the following weights:

| Dimension | Weight |
|---|---:|
| Cost Efficiency | 40% |
| Overall Quality | 35% |
| Operational Risk | 25% |

### Cost Efficiency

The Cost Agent uses:

- 75% Unit Price competitiveness
- 25% Payment Terms

### Overall Quality

The Quality Agent uses:

- 40% Quality Score
- 30% Defect Performance
- 30% Past Performance

### Operational Risk

The Risk Agent uses:

- 40% Risk Level
- 30% Delivery Reliability
- 20% Lead Time
- 10% Annual Capacity

### Overall Procurement Score

```text
Overall Procurement Score =
    40% Cost Efficiency
  + 35% Overall Quality
  + 25% Operational Risk
```

Higher scores indicate a stronger overall procurement profile under the selected weighting.

## What-If Simulator

The What-If Simulator allows users to change the importance of Cost, Quality and Risk.

Available scenarios:

| Scenario | Cost | Quality | Risk |
|---|---:|---:|---:|
| Balanced | 40% | 35% | 25% |
| Cost Focused | 60% | 25% | 15% |
| Quality Focused | 25% | 50% | 25% |
| Risk Focused | 25% | 25% | 50% |
| Custom | User-defined | User-defined | User-defined |

This allows procurement managers to understand how supplier recommendations change when business priorities change.

## Procurement Copilot

The Procurement Copilot uses the current supplier analysis as context and provides natural-language answers.

The system is designed to answer using the available supplier information rather than generating unsupported supplier facts.

When the local AI model is unavailable, the application uses deterministic fallback responses for common procurement questions.

## Dataset

The demonstration dataset is stored in:

```text
data/supplier_data.csv
```

It contains supplier-level information including:

```text
Supplier_ID
Supplier_Name
Category
Unit_Price
Quality_Score
Defect_Rate
Delivery_Reliability
Lead_Time_Days
Risk_Level
Payment_Terms_Days
Annual_Capacity
Past_Performance_Score
```

The application also supports uploading a supplier dataset through the Streamlit interface.

## Technology Stack

- Python
- Pandas
- NumPy
- Streamlit
- Plotly
- Ollama
- Llama 3.2:3b
- python-dotenv
- CSV

## Project Structure

```text
AI_Procurement_Advisor/
│
├── agents/
│   ├── cost_agent.py
│   ├── quality_agent.py
│   ├── risk_agent.py
│   ├── procurement_agent.py
│   ├── orchestrator.py
│   └── copilot_agent.py
│
├── data/
│   └── supplier_data.csv
│
├── outputs/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/Chirag20-gg/AI_Procurement_Advisor.git
```

### 2. Open the project directory

```bash
cd AI_Procurement_Advisor
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in the browser.

## Local AI Model

The project can use Ollama with:

```text
llama3.2:3b
```

The local model is used mainly for:

- Procurement strategy explanations
- Procurement Copilot responses

The numerical supplier scoring and ranking are handled using deterministic Python logic.

This separation keeps the core procurement analysis reproducible.

## Cloud Deployment

The application is deployed using Streamlit Community Cloud.

The cloud version can continue to operate even when the local Ollama runtime is unavailable because the project includes deterministic fallback logic.

## Public Application

[Open AI Procurement Advisor](https://aiprocurementadvisor-xyfccbayr28keww7y3uajn.streamlit.app/)

## Key Features

- Multi-agent procurement analysis
- Cost evaluation
- Quality evaluation
- Operational risk evaluation
- Supplier ranking
- Automated supplier recommendation
- What-If analysis
- Custom procurement weights
- Procurement Copilot
- Demo dataset
- CSV dataset upload
- Streamlit dashboard
- Local LLM support
- Cloud-safe fallback

## Example Use Case

A procurement manager needs to select a supplier for packaging materials.

Instead of looking only at unit price, the system evaluates:

```text
Cost
   +
Quality
   +
Operational Risk
   ↓
Overall Procurement Score
   ↓
Supplier Ranking
   ↓
Recommendation
```

The manager can then change the scenario to see whether the recommendation remains the same when cost, quality or risk becomes more important.

## Limitations

- The demonstration dataset is synthetic.
- The current dataset contains a limited number of suppliers.
- Supplier rankings depend on the selected scoring weights.
- The application does not create purchase orders.
- The application does not execute procurement transactions.
- There is no live ERP integration.
- Final procurement decisions should be reviewed by a human decision-maker.

## Future Scope

Potential future improvements include:

- Excel file support
- Historical supplier performance analysis
- Supplier-specific benchmarks
- Predictive supplier risk modelling
- Contract and supplier document analysis
- ERP integration
- Supplier disruption prediction
- Role-based access control
- Procurement approval workflows
- Audit logging
- Advanced sourcing and negotiation support

## License

This project is intended for educational and demonstration purposes.
```





