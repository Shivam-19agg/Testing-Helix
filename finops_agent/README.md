# FinOps Agent for Azure

This project is an AI-powered FinOps agent designed to analyze Azure environments and provide cost-saving recommendations for Azure API Management (APIM) instances. It is built using a context-engineered, multi-agent architecture with LangGraph.

## Architecture

The agent's architecture is based on five core principles from Context Engineering:
- **Isolate Context**: Each agent (node) performs a specific task and only receives the context it needs.
- **Offload Context**: Detailed information is written to a Git-based audit log, keeping the in-memory state lightweight.
- **Reduce Context**: Nodes summarize their findings before passing the state to the next step.
- **Retrieve Context**: Remediation workflows retrieve only the specific, approved recommendation they need to act on.
- **Cache Context**: Static, frequently used information is cached to avoid repeated fetching.

## Workflows

The agent has two main workflows:
1.  **Analysis Workflow**: Scans the environment and generates recommendations.
2.  **Remediation Workflow**: Applies approved recommendations.

## Getting Started

### Prerequisites

- Python 3.10+
- An Azure subscription with API Management instances

### Installation

1.  Clone the repository.
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Agent

To run the analysis workflow (currently with placeholder data), execute the orchestrator as a module from the project root directory:
```bash
python -m finops_agent.orchestrator
```
