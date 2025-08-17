# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Traigent SDK** is an enterprise-grade LLM optimization platform that helps developers find optimal AI configurations for their specific use cases. It provides zero-code integration through decorators and supports multiple execution modes (local, cloud, hybrid).

## Core Architecture

### Main Package Structure (`traigent/`)
- **`api/`** - Public API layer with decorators (`@traigent.optimize`) and functions
- **`core/`** - Core orchestration logic and optimized function handling 
- **`optimizers/`** - Optimization algorithms (grid, random, Bayesian, cloud-based)
- **`evaluators/`** - Evaluation framework with metrics tracking
- **`integrations/`** - Framework plugins (LangChain, OpenAI SDK, Anthropic)
- **`cloud/`** - Cloud service integration and backend communication
- **`config/`** - Configuration management and API key handling
- **`analytics/`** - Privacy-safe analytics and predictive intelligence
- **`security/`** - Enterprise security features and encryption
- **`storage/`** - Local storage for optimization results

### Key Concepts
- **Adaptive Variables** - Configuration parameters that change based on objectives (model, temperature, etc.)
- **Configuration Space** - The search space of parameter combinations to test
- **Seamless Mode** - Zero-code optimization via automatic parameter interception  
- **Parameter Mode** - Explicit configuration access for advanced users
- **Execution Modes** - Local (privacy-first), Cloud (advanced optimization), Hybrid (balanced)

## Development Commands

### Installation & Setup
```bash
# Clone and basic setup
git clone https://github.com/nimrodbusany/Traigent.git
cd Traigent
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements/requirements.txt
pip install -e .

# For development
pip install -r requirements/requirements-dev.txt

# For framework integrations  
pip install -r requirements/requirements-integrations.txt

# For all features
pip install -r requirements/requirements-all.txt
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/     # Unit tests only
python -m pytest tests/integration/  # Integration tests
python -m pytest tests/e2e/     # End-to-end tests

# Quick smoke tests
python -m pytest tests/unit/api/test_types.py -v -x

# Run with coverage
python -m pytest tests/unit -q --cov=traigent --cov-report=html

# Use the comprehensive test script
./scripts/run_tests.sh
```

### Code Quality
```bash
# Format code
ruff format traigent/
black traigent/

# Lint code  
ruff check traigent/
flake8 traigent/

# Type checking
mypy traigent/

# Install pre-commit hooks
pre-commit install
```

### Running Examples & Playground
```bash
# Launch interactive UI
python scripts/launch_control_center.py

# Run basic examples
cd examples/quickstart
python hello_traigent.py

# Run framework integration examples
cd examples/integrations/langchain/examples/sentiment_classification
python function.py

# Run use case examples  
cd examples/use-cases/by-domain/nlp/classification/sentiment_analysis_optimization
python basic_sentiment_tuning.py
```

## Project Configuration

### Environment Setup
The project uses `.env` files for configuration:
```bash
# Copy template and configure
cp .env.example .env

# Required environment variables:
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key  
TRAIGENT_API_KEY=your-traigent-key  # For cloud mode
TRAIGENT_EXECUTION_MODE=local  # local, cloud, or hybrid
TRAIGENT_RESULTS_FOLDER=~/.traigent/results
```

### Key Configuration Files
- **`pyproject.toml`** - Main project configuration with dependencies and tool settings
- **`pytest.ini`** - Test configuration with coverage settings (85% minimum)
- **`requirements/`** - Modular dependency management by feature set

## API Usage Patterns

### Basic Optimization Pattern
```python
import traigent

@traigent.optimize(
    configuration_space={
        "model": ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"],
        "temperature": [0.1, 0.5, 0.9]
    },
    eval_dataset="your_data.jsonl",
    objectives=["accuracy", "cost"]
)
def your_function(input_text: str) -> str:
    # Your existing code - TraiGent intercepts and optimizes
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    return llm.invoke(input_text).content
```

### Framework Integration Pattern
TraiGent automatically detects and optimizes:
- **LangChain** - `ChatOpenAI()`, `vectorstore.similarity_search()`, chains
- **OpenAI SDK** - `openai.chat.completions.create()`
- **Anthropic SDK** - `anthropic.messages.create()`

### Cloud vs Local Modes
- **Local Mode** - All data stays local, basic optimization algorithms
- **Cloud Mode** - Advanced Bayesian optimization with cloud intelligence  
- **Hybrid Mode** - Local execution with cloud optimization guidance

## Testing Architecture

### Test Organization
- **`tests/unit/`** - Fast unit tests by module (api, core, optimizers, etc.)
- **`tests/integration/`** - Cross-module integration tests
- **`tests/e2e/`** - End-to-end workflow tests
- **`tests/security/`** - Security and authentication tests
- **`tests/performance/`** - Performance benchmarking tests

### Test Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.slow` - Slow tests (skip with `-m "not slow"`)
- `@pytest.mark.asyncio` - Async tests

### Coverage Requirements
- Minimum 85% code coverage enforced
- HTML coverage reports generated in `htmlcov/`
- XML coverage for CI/CD integration

## Framework Integration Guidelines

### Adding New Framework Support
1. Create plugin in `traigent/integrations/llms/`
2. Implement parameter interception for framework calls
3. Add to `framework_override.py` detection logic
4. Create examples in `examples/integrations/`
5. Add tests in `tests/unit/integrations/`

### Plugin Architecture
- **Base Plugin** - `traigent/integrations/base_plugin.py`
- **Discovery** - Automatic framework detection
- **Override** - Parameter interception and replacement during optimization

## Security Considerations

### Enterprise Security Features
- JWT-based authentication (`traigent/security/jwt_validator.py`)
- Tenant isolation (`traigent/security/tenant.py`)
- Audit logging (`traigent/security/audit.py`)
- Rate limiting (`traigent/security/rate_limiter.py`)
- Encryption utilities (`traigent/security/crypto_utils.py`)

### Privacy-Safe Analytics
- No sensitive data collection (no code content, API keys, or parameters)
- Only aggregated usage patterns and performance metrics
- Local storage option for complete privacy

## Common Development Tasks

### Adding a New Optimizer
1. Inherit from `traigent/optimizers/base.py`
2. Implement `suggest_trial()` and `report_result()` methods
3. Register in `traigent/optimizers/registry.py`
4. Add tests in `tests/unit/optimizers/`

### Adding Custom Evaluators
1. Inherit from `traigent/evaluators/base.py`
2. Implement `evaluate()` method for your metrics
3. Add to examples with dataset and configuration

### Debugging Optimization Issues
1. Check logs in `~/.traigent/logs/`
2. Verify configuration space parameters
3. Test with minimal dataset first
4. Use `execution_mode="local"` for debugging
5. Check API key configuration in `.env`

## Performance Considerations

### Optimization Performance
- Grid search: Exhaustive but slow for large spaces
- Random search: Good baseline performance
- Bayesian optimization: Best for complex parameter spaces (cloud mode)
- Interactive optimizer: Real-time optimization with user feedback

### Dataset Handling
- Intelligent subset selection reduces costs by 60-80%
- Adaptive sampling based on optimization progress
- Automatic dataset validation and formatting

## Deployment Patterns

### Local Development
- Use local execution mode for initial development
- Enable detailed logging for debugging
- Test with small datasets first

### Production Deployment  
- Cloud or hybrid mode for advanced optimization
- Configure proper authentication and rate limiting
- Monitor usage through privacy-safe analytics
- Use enterprise security features for multi-tenant deployments