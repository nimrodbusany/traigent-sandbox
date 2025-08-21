# TraiGent Agent Library

This directory contains modular agents that can be optimized using TraiGent's intelligent parameter search.

## Directory Structure

Each agent is contained in its own folder with three required files:

```
agents/
├── agent_name/
│   ├── agent.py       # The agent implementation
│   ├── config.json    # Agent configuration and parameter space
│   └── dataset.json   # Benchmark dataset for evaluation
└── README.md          # This file
```

## Available Agents

### support_classifier
Customer support ticket classification into technical, billing, or general categories.

## Creating a New Agent

To create a new agent:

1. Create a new folder under `agents/` with your agent name
2. Create `agent.py` with:
   - An Agent class with a `create_function()` method
   - A `PromptBuilder` class for building prompts
   - An `ExampleSelector` class for few-shot examples
3. Create `config.json` with:
   - Agent metadata (name, description, version)
   - Parameter definitions and default values
   - Objectives for optimization
4. Create `dataset.json` with:
   - Examples in format: `{"input": {...}, "output": "..."}`
   - Metadata about the dataset

## Using Agents

### List available agents:
```bash
python traigent_cli.py --list-agents
```

### Run optimization with an agent:
```bash
python traigent_cli.py --agent support_classifier
```

### Interactive mode (select agent from menu):
```bash
python traigent_cli.py
```

## Agent Configuration Format

The `config.json` file should follow this structure:

```json
{
  "name": "Agent Name",
  "description": "Agent description",
  "version": "1.0.0",
  "objectives": ["accuracy"],
  "parameters": {
    "param_name": {
      "type": "categorical|continuous|discrete|boolean",
      "values": [...],
      "default": ...,
      "description": "Parameter description"
    }
  },
  "parameter_categories": {
    "Category Name": ["param1", "param2"]
  }
}
```

## Dataset Format

The `dataset.json` file should follow this structure:

```json
{
  "metadata": {
    "description": "Dataset description",
    "total_examples": 100
  },
  "examples": [
    {
      "input": {"text": "input text"},
      "output": "expected output",
      "difficulty": "easy|medium|hard|expert" 
    }
  ]
}
```