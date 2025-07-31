# Agent Instructions

This document provides instructions and conventions for the AI agent working on this codebase.

## Project Structure

- `finops_agent/`: The main Python package containing the application logic.
  - `orchestrator.py`: The main LangGraph workflow definition.
  - `nodes/`: Contains all the agent nodes, separated into `analysis` and `execution`. Each node should be in its own file.
  - `tools/`: Utility functions, especially for interacting with Azure APIs.
- `tests/`: Contains all unit and integration tests. Test structure should mirror the main package structure.
- `requirements.txt`: Project dependencies.

## Development Workflow

1.  **Node Implementation**: When implementing a new analysis or execution node (as per the Work Items), create a new file in the appropriate subdirectory under `finops_agent/nodes/`.
2.  **Isolation**: Nodes should be self-contained. They receive the state, perform their function, and return only the portion of the state they have modified. They should not have dependencies on other nodes.
3.  **State Management**: The `AgentState` type hint is defined in `orchestrator.py`. For now, nodes should operate on the state as a dictionary (`Dict[str, Any]`) to avoid circular import issues. Be robust to missing keys by using `state.get('key', default_value)`.
4.  **Testing**:
    - All new nodes must have corresponding unit tests in the `tests/` directory.
    - Before submitting, run the orchestrator to ensure the new node integrates correctly with the graph.

## Running the Code

- To run the main orchestrator, execute it as a module from the `finops_agent` project root directory:
  ```bash
  python -m finops_agent.orchestrator
  ```
- This ensures that Python's import paths are set up correctly for the package structure, using relative imports within the package.
