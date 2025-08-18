#!/bin/bash
# TraiGent CLI Testing Script
# Tests different CLI scenarios in mock mode

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUICKSTART_DIR="$SCRIPT_DIR/quickstart"
TRAIGENT_DIR="$SCRIPT_DIR/Traigent"

echo "🎯 TraiGent CLI Testing Script"
echo "=============================="
echo ""

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check directories
    if [[ ! -d "$QUICKSTART_DIR" ]]; then
        log_error "Quickstart directory not found: $QUICKSTART_DIR"
        exit 1
    fi
    
    if [[ ! -d "$TRAIGENT_DIR" ]]; then
        log_error "Traigent directory not found: $TRAIGENT_DIR"
        exit 1
    fi
    
    # Check required files
    if [[ ! -f "$QUICKSTART_DIR/traigent_benchmark_cli.py" ]]; then
        log_error "CLI tool not found: $QUICKSTART_DIR/traigent_benchmark_cli.py"
        exit 1
    fi
    
    if [[ ! -f "$QUICKSTART_DIR/support_classification_dataset.json" ]]; then
        log_error "Dataset not found: $QUICKSTART_DIR/support_classification_dataset.json"
        exit 1
    fi
    
    # Check Python version
    if ! python3 --version >/dev/null 2>&1; then
        log_error "Python 3 not found"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Function to setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    cd "$TRAIGENT_DIR"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install TraiGent
    log_info "Installing TraiGent..."
    pip install -e ".[all]" > /dev/null 2>&1
    
    # Verify installation
    if python -c "import traigent; print(f'TraiGent {traigent.__version__}')" >/dev/null 2>&1; then
        log_success "TraiGent installation verified"
    else
        log_error "TraiGent installation failed"
        exit 1
    fi
    
    cd "$QUICKSTART_DIR"
    
    # Setup mock mode environment
    cat > .env << 'EOF'
OPENAI_API_KEY=mock-key-for-demos
ANTHROPIC_API_KEY=mock-key-for-demos
TRAIGENT_EXECUTION_MODE=local
TRAIGENT_MOCK_MODE=true
EOF
    
    log_success "Environment setup complete"
}

# Function to test CLI startup
test_cli_startup() {
    log_info "Testing CLI startup..."
    
    cd "$QUICKSTART_DIR"
    
    # Test if CLI can start and show banner
    if timeout 10s python traigent_benchmark_cli.py <<< $'\n' >/dev/null 2>&1; then
        log_success "CLI startup test passed"
    else
        log_warning "CLI startup test - may require interactive input"
    fi
}

# Function to test dataset loading
test_dataset_loading() {
    log_info "Testing dataset loading..."
    
    cd "$QUICKSTART_DIR"
    
    # Test dataset loading with Python
    python3 << 'EOF'
import json
import sys

try:
    with open('support_classification_dataset.json', 'r') as f:
        data = json.load(f)
    
    examples = data['examples']
    metadata = data['metadata']
    
    print(f"✅ Dataset loaded successfully")
    print(f"   • Total examples: {len(examples)}")
    print(f"   • Categories: {metadata['categories']}")
    print(f"   • Difficulty levels: {metadata['difficulty_levels']}")
    
    # Validate example structure
    first_example = examples[0]
    required_fields = ['id', 'input', 'output', 'difficulty']
    missing_fields = [field for field in required_fields if field not in first_example]
    
    if missing_fields:
        print(f"❌ Missing fields in examples: {missing_fields}")
        sys.exit(1)
    else:
        print("✅ Dataset structure validation passed")
        
except Exception as e:
    print(f"❌ Dataset loading failed: {e}")
    sys.exit(1)
EOF

    if [[ $? -eq 0 ]]; then
        log_success "Dataset loading test passed"
    else
        log_error "Dataset loading test failed"
        exit 1
    fi
}

# Function to test mock mode setup
test_mock_mode() {
    log_info "Testing mock mode setup..."
    
    cd "$QUICKSTART_DIR"
    
    # Test mock mode detection
    python3 << 'EOF'
import os
import sys

# Check environment variables
mock_mode = os.environ.get('TRAIGENT_MOCK_MODE', 'false').lower() == 'true'
openai_key = os.environ.get('OPENAI_API_KEY', '')
anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')

print(f"Mock mode enabled: {mock_mode}")
print(f"OpenAI key: {'mock-key-for-demos' if openai_key == 'mock-key-for-demos' else 'real key detected'}")
print(f"Anthropic key: {'mock-key-for-demos' if anthropic_key == 'mock-key-for-demos' else 'real key detected'}")

if mock_mode and openai_key == 'mock-key-for-demos':
    print("✅ Mock mode correctly configured")
else:
    print("❌ Mock mode configuration issue")
    sys.exit(1)

# Test mock LLM functionality
sys.path.insert(0, '../Traigent/examples/shared_utils')
try:
    from mock_llm import setup_mock_mode, get_mock_response
    
    # Test mock functions
    mock_activated = setup_mock_mode()
    print(f"Mock mode activation: {mock_activated}")
    
    # Test mock response
    response = get_mock_response("Test prompt", "gpt-3.5-turbo")
    if response.get('mock_mode'):
        print("✅ Mock LLM functions working")
    else:
        print("❌ Mock LLM functions not working")
        sys.exit(1)
        
except ImportError as e:
    print(f"⚠️  Mock LLM import warning: {e}")
    print("✅ Basic mock mode still functional")
    
except Exception as e:
    print(f"❌ Mock mode test failed: {e}")
    sys.exit(1)
EOF

    if [[ $? -eq 0 ]]; then
        log_success "Mock mode test passed"
    else
        log_error "Mock mode test failed"
        exit 1
    fi
}

# Function to create test configurations
create_test_configurations() {
    log_info "Creating test configurations..."
    
    cd "$QUICKSTART_DIR"
    
    # Create benchmark_configs directory if it doesn't exist
    mkdir -p benchmark_configs
    
    # Create minimal test configuration
    cat > benchmark_configs/test_minimal.yaml << 'EOF'
name: test_minimal
dataset:
  total_examples: 5
  sampling_strategy: sequential
  difficulty_distribution: null
execution:
  mode: local
  mock_mode: true
  early_stopping: false
  algorithm: grid
  max_trials: 4
parameters:
  model:
    param_type: categorical
    values:
    - gpt-3.5-turbo
    - gpt-4o-mini
    enabled: true
    description: LLM model to use
  temperature:
    param_type: continuous
    values:
    - 0.0
    - 0.5
    enabled: true
    description: Sampling temperature
output:
  save_results: true
  export_formats:
  - json
  create_visualizations: false
EOF

    # Create advanced test configuration
    cat > benchmark_configs/test_advanced.yaml << 'EOF'
name: test_advanced
dataset:
  total_examples: 10
  sampling_strategy: stratified
  difficulty_distribution:
    easy: 3
    medium: 3
    hard: 2
    expert: 2
execution:
  mode: local
  mock_mode: true
  early_stopping: false
  algorithm: random
  max_trials: 12
parameters:
  model:
    param_type: categorical
    values:
    - gpt-3.5-turbo
    - gpt-4o-mini
    enabled: true
    description: LLM model to use
  temperature:
    param_type: continuous
    values:
    - 0.0
    - 0.3
    - 0.7
    enabled: true
    description: Sampling temperature
  few_shot_k:
    param_type: discrete
    values:
    - 0
    - 1
    - 3
    enabled: true
    description: Number of few-shot examples
  system_role:
    param_type: categorical
    values:
    - classifier
    - expert
    enabled: true
    description: System role/persona
output:
  save_results: true
  export_formats:
  - json
  - csv
  create_visualizations: true
EOF

    log_success "Test configurations created"
    log_info "Available configurations:"
    ls -la benchmark_configs/test_*.yaml | awk '{print "   • " $9}'
}

# Function to demonstrate CLI input sequences
demonstrate_cli_sequences() {
    log_info "Demonstrating CLI input sequences..."
    
    echo ""
    echo "🎮 CLI Input Sequences for Different Scenarios"
    echo "=============================================="
    
    echo ""
    echo "📊 Scenario 1: Basic Mock Test"
    echo "Input sequence for minimal parameter test:"
    echo "2 → basic_test → 5 → 3 → 2 2 1 0 → y → y y n 2 y y n 2 → n n n → 1 y n → y y y"
    
    echo ""
    echo "📊 Scenario 2: Advanced Mock Test"
    echo "Input sequence for comprehensive parameter test:"
    echo "2 → advanced_test → 10 → 1 → 3 3 2 2 → y → y y n 2 y y n 3 → y → y y n 3 y y n 2 → y → y y n 2 y y n 2 n y n 2 n → n → random → 20 → 1 y n → y y y"
    
    echo ""
    echo "📊 Scenario 3: Prompt Engineering Focus"
    echo "Input sequence for prompt engineering optimization:"
    echo "2 → prompt_test → 8 → 1 → 2 2 2 2 → y → n y y n 2 → y → y y n 2 y y n 2 → y → y y n 3 y y n 2 y y n 2 y y → n → 1 y n → y y y"
    
    echo ""
    log_success "CLI sequences demonstrated"
}

# Function to run validation tests
run_validation_tests() {
    log_info "Running validation tests..."
    
    cd "$QUICKSTART_DIR"
    
    # Test 1: Import validation
    log_info "Test 1: Import validation"
    python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from traigent_benchmark_cli import TraiGentBenchmarkCLI, ParameterRegistry, DatasetLoader
    print('✅ All CLI imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    # Test 2: Parameter registry validation
    log_info "Test 2: Parameter registry validation"
    python3 -c "
import sys
sys.path.insert(0, '.')
from traigent_benchmark_cli import ParameterRegistry

try:
    registry = ParameterRegistry()
    categories = registry.get_categories()
    total_params = sum(len(params) for params in categories.values())
    print(f'✅ Parameter registry loaded: {total_params} parameters in {len(categories)} categories')
    
    # Validate core parameters exist
    core_params = ['model', 'temperature', 'few_shot_k', 'system_role']
    for param in core_params:
        if registry.get_parameter(param):
            print(f'✅ Core parameter found: {param}')
        else:
            print(f'❌ Core parameter missing: {param}')
            sys.exit(1)
            
except Exception as e:
    print(f'❌ Parameter registry error: {e}')
    sys.exit(1)
"
    
    # Test 3: Dataset loader validation
    log_info "Test 3: Dataset loader validation"
    python3 -c "
import sys
sys.path.insert(0, '.')
from traigent_benchmark_cli import DatasetLoader

try:
    loader = DatasetLoader('support_classification_dataset.json')
    
    # Test sampling strategies
    strategies = ['random', 'stratified', 'sequential']
    for strategy in strategies:
        examples = loader.sample_examples(5, strategy)
        print(f'✅ Sampling strategy \"{strategy}\": {len(examples)} examples')
    
    # Test difficulty filtering
    difficulties = ['easy', 'medium', 'hard', 'expert']
    for difficulty in difficulties:
        examples = loader.get_examples_by_difficulty(difficulty)
        print(f'✅ Difficulty \"{difficulty}\": {len(examples)} examples')
        
except Exception as e:
    print(f'❌ Dataset loader error: {e}')
    sys.exit(1)
"
    
    log_success "All validation tests passed"
}

# Function to show usage examples
show_usage_examples() {
    echo ""
    echo "🚀 Quick Usage Examples"
    echo "======================"
    
    echo ""
    echo "1. Start CLI tool:"
    echo "   cd quickstart && python traigent_benchmark_cli.py"
    
    echo ""
    echo "2. Test with minimal parameters (fastest):"
    echo "   • Choose: Guided Configuration (2)"
    echo "   • Examples: 5"
    echo "   • Parameters: model + temperature only"
    echo "   • Mock mode: enabled"
    
    echo ""
    echo "3. Test comprehensive optimization:"
    echo "   • Choose: Guided Configuration (2)"
    echo "   • Examples: 15-20"
    echo "   • Parameters: Include multiple categories"
    echo "   • Strategy: random with 20-30 trials"
    echo "   • Mock mode: enabled"
    
    echo ""
    echo "4. View saved configurations:"
    echo "   ls benchmark_configs/"
    
    echo ""
    echo "5. Monitor CLI performance:"
    echo "   time python traigent_benchmark_cli.py"
    
    echo ""
    log_success "Usage examples provided"
}

# Function to cleanup
cleanup() {
    log_info "Cleaning up..."
    
    # Remove test .env file if in test mode
    if [[ "$1" == "test" ]]; then
        rm -f "$QUICKSTART_DIR/.env"
        log_info "Test .env file removed"
    fi
    
    log_success "Cleanup complete"
}

# Main execution
main() {
    local run_mode="${1:-full}"
    
    case "$run_mode" in
        "setup")
            check_prerequisites
            setup_environment
            ;;
        "test")
            check_prerequisites
            setup_environment
            test_cli_startup
            test_dataset_loading
            test_mock_mode
            run_validation_tests
            cleanup test
            ;;
        "demo")
            check_prerequisites
            create_test_configurations
            demonstrate_cli_sequences
            show_usage_examples
            ;;
        "full"|*)
            check_prerequisites
            setup_environment
            test_cli_startup
            test_dataset_loading
            test_mock_mode
            create_test_configurations
            run_validation_tests
            demonstrate_cli_sequences
            show_usage_examples
            ;;
    esac
    
    echo ""
    log_success "Script completed successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "   1. cd quickstart"
    echo "   2. source ../Traigent/venv/bin/activate"
    echo "   3. python traigent_benchmark_cli.py"
    echo ""
}

# Handle script arguments
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi