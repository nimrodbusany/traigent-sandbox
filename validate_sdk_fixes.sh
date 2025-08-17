#!/usr/bin/bash
# TraiGent SDK Validation Script
# Tests the complete new user experience after SDK team fixes
# Run this from the project root directory

set -e  # Exit on any error

echo "🧪 TraiGent SDK New User Experience Validation"
echo "=============================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TEST_DIR="sdk_validation_test"
REPO_URL="https://github.com/nimrodbusany/Traigent.git"

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✅ SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠️  WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[❌ ERROR]${NC} $1"
}

# Function to check if command succeeded
check_result() {
    if [ $? -eq 0 ]; then
        print_success "$1"
    else
        print_error "$1 FAILED"
        exit 1
    fi
}

# Start validation
print_status "Starting fresh environment validation..."

# 1. Clean up any existing test directory
print_status "Step 1: Cleaning up previous test runs"
rm -rf "$TEST_DIR"
mkdir "$TEST_DIR"
cd "$TEST_DIR"

# 2. Create fresh virtual environment
print_status "Step 2: Creating fresh virtual environment"
python3 -m venv fresh_venv
source fresh_venv/bin/activate
check_result "Virtual environment created and activated"

# 3. Test TraiGent installation with examples
print_status "Step 3: Installing TraiGent SDK with examples from GitHub"
pip install "git+${REPO_URL}#egg=traigent[examples]" > install.log 2>&1
check_result "TraiGent SDK installation"

# 4. Test dependency imports
print_status "Step 4: Testing critical dependency imports"
python3 -c "
import traigent
from langchain_openai import ChatOpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
import pandas as pd
import numpy as np
print('✅ All critical dependencies imported successfully')
" 2>/dev/null
check_result "Dependency imports"

# 5. Clone repo for examples (since we need the examples directory)
print_status "Step 5: Cloning TraiGent repo for examples"
git clone "$REPO_URL" traigent_repo > clone.log 2>&1
check_result "Repository cloning"

# 6. Copy .env file if it exists in parent directory
print_status "Step 6: Setting up environment variables"
if [ -f "../.env" ]; then
    cp "../.env" "traigent_repo/examples/.env"
    print_success "Environment file copied"
else
    print_warning "No .env file found in parent directory - creating mock one"
    cat > traigent_repo/examples/.env << EOF
OPENAI_API_KEY=sk-test-key-for-validation
ANTHROPIC_API_KEY=sk-ant-test-key-for-validation
TRAIGENT_API_KEY=sk-traigent-test-key-for-validation
TRAIGENT_MOCK_MODE=true
EOF
fi

# 7. Test hello_traigent.py example
print_status "Step 7: Testing hello_traigent.py example"
cd traigent_repo/examples
export TRAIGENT_MOCK_MODE=true
export PYTHONPATH="$(pwd)"

echo "Testing hello_traigent.py..."
timeout 60 python quickstart/hello_traigent.py > hello_test.log 2>&1
HELLO_RESULT=$?

if [ $HELLO_RESULT -eq 0 ]; then
    print_success "hello_traigent.py executed successfully"
    
    # Check for expected output patterns
    if grep -q "TraiGent Hello World" hello_test.log; then
        print_success "Found expected output: 'TraiGent Hello World'"
    else
        print_warning "Expected output pattern not found in hello_traigent.py"
    fi
    
    if grep -q "analyze_sentiment" hello_test.log; then
        print_success "Sentiment analysis functions working"
    else
        print_warning "Sentiment analysis output not detected"
    fi
else
    print_error "hello_traigent.py execution failed"
    echo "--- Error Log ---"
    cat hello_test.log
    echo "--- End Error Log ---"
fi

# 8. Test basic_optimization.py example  
print_status "Step 8: Testing basic_optimization.py example"
echo "Testing basic_optimization.py (may take 30-60 seconds)..."
timeout 90 python quickstart/basic_optimization.py > basic_test.log 2>&1
BASIC_RESULT=$?

if [ $BASIC_RESULT -eq 0 ]; then
    print_success "basic_optimization.py executed successfully"
    
    # Check for optimization results
    if grep -q "Best configuration:" basic_test.log; then
        print_success "Found optimization results"
        BEST_CONFIG=$(grep "Best configuration:" basic_test.log)
        echo "    ${BEST_CONFIG}"
    else
        print_warning "Optimization results not found"
    fi
    
    if grep -q "Best accuracy:" basic_test.log; then
        ACCURACY=$(grep "Best accuracy:" basic_test.log)
        echo "    ${ACCURACY}"
        
        # Check if accuracy is not 0.0%
        if echo "$ACCURACY" | grep -q "0.0%"; then
            print_warning "Accuracy is 0.0% - may indicate evaluation issue"
        else
            print_success "Non-zero accuracy detected - evaluation working"
        fi
    else
        print_warning "Accuracy results not found"
    fi
    
    # Check for error patterns
    if grep -qi "error\|failed\|exception" basic_test.log; then
        print_warning "Detected error messages in optimization log"
        echo "--- Error patterns found ---"
        grep -i "error\|failed\|exception" basic_test.log | head -5
        echo "--- End error patterns ---"
    fi
    
else
    print_error "basic_optimization.py execution failed"
    echo "--- Error Log ---"
    cat basic_test.log
    echo "--- End Error Log ---"
fi

# 9. Comprehensive Example Testing
print_status "Step 9: Comprehensive Example Testing"
cd "../.."

# Create comprehensive test results
echo "📊 COMPREHENSIVE EXAMPLE TESTING" > comprehensive_test_results.md
echo "================================" >> comprehensive_test_results.md
echo "" >> comprehensive_test_results.md
echo "**Date**: $(date)" >> comprehensive_test_results.md
echo "**Total Examples Found**: $(find traigent_repo/examples -name "*.py" -type f | wc -l)" >> comprehensive_test_results.md
echo "" >> comprehensive_test_results.md

# Test results counters
TOTAL_TESTED=0
SUCCESSFUL_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Function to test an example
test_example() {
    local example_path="$1"
    local relative_path="$example_path"
    local example_name=$(basename "$example_path" .py)
    local example_dir=$(dirname "$example_path")
    
    print_status "Testing: $relative_path"
    TOTAL_TESTED=$((TOTAL_TESTED + 1))
    
    # Skip utility files and __init__.py files
    if [[ "$example_name" == "__init__" ]] || [[ "$example_name" == *"_utils" ]] || [[ "$example_name" == *"_helper" ]]; then
        print_status "  Skipped: Utility file"
        SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
        echo "- ⏭️  SKIPPED: $relative_path (utility file)" >> ../../../comprehensive_test_results.md
        return 0
    fi
    
    # Create test log file
    local log_file="test_$(echo "$relative_path" | tr '/' '_' | tr '.' '_').log"
    
    # Set up environment for this test
    cd "$example_dir"
    export PYTHONPATH="$(pwd):$(dirname $(pwd)):$PYTHONPATH"
    export TRAIGENT_MOCK_MODE=true
    
    # Try to run the example with timeout
    timeout 60 python "$example_name.py" > "../../../$log_file" 2>&1
    local result=$?
    
    # Check result
    if [ $result -eq 0 ]; then
        print_success "  ✅ SUCCESS: $relative_path"
        SUCCESSFUL_TESTS=$((SUCCESSFUL_TESTS + 1))
        echo "- ✅ SUCCESS: $relative_path" >> "../../../comprehensive_test_results.md"
        
        # Check for specific success patterns
        if grep -q "optimization.*complete\|best.*configuration\|accuracy\|TraiGent" "../../../$log_file" 2>/dev/null; then
            echo "  └─ Contains expected optimization output" >> "../../../comprehensive_test_results.md"
        fi
        
    elif [ $result -eq 124 ]; then
        print_warning "  ⏰ TIMEOUT: $relative_path"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "- ⏰ TIMEOUT: $relative_path (>60s)" >> "../../../comprehensive_test_results.md"
        
    else
        print_error "  ❌ FAILED: $relative_path"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "- ❌ FAILED: $relative_path" >> "../../../comprehensive_test_results.md"
        
        # Extract key error information
        if [ -f "../../../$log_file" ]; then
            error_info=$(grep -i "error\|exception\|traceback" "../../../$log_file" | head -2)
            if [ ! -z "$error_info" ]; then
                echo "  └─ Error: $error_info" >> "../../../comprehensive_test_results.md"
            fi
        fi
    fi
    
    # Return to examples directory base
    cd - > /dev/null
}

# Set up environment for comprehensive testing
EXAMPLES_DIR="traigent_repo/examples"
cd "$EXAMPLES_DIR"
export PYTHONPATH="$(pwd):$PYTHONPATH"
export TRAIGENT_MOCK_MODE=true

# Priority 1: Test quickstart examples (most critical)
print_status "Priority 1: Testing quickstart examples"
echo "" >> ../../comprehensive_test_results.md
echo "## 🚀 Priority 1: Quickstart Examples" >> ../../comprehensive_test_results.md
echo "" >> ../../comprehensive_test_results.md

for example in $(find quickstart -name "*.py" -type f); do
    test_example "$example"
done

# Priority 2: Test learn-traigent core concepts
print_status "Priority 2: Testing learn-traigent core concepts"
echo "" >> ../../comprehensive_test_results.md
echo "## 📚 Priority 2: Learn TraiGent - Core Concepts" >> ../../comprehensive_test_results.md
echo "" >> ../../comprehensive_test_results.md

for example in $(find learn-traigent/core-concepts -name "*.py" -type f 2>/dev/null | head -10); do
    test_example "$example"
done

# Priority 3: Test main.py files (primary examples)
print_status "Priority 3: Testing main example entry points"
echo "" >> ../../comprehensive_test_results.md
echo "## 🎯 Priority 3: Main Example Entry Points" >> ../../comprehensive_test_results.md
echo "" >> ../../comprehensive_test_results.md

for example in $(find . -name "main.py" -type f | head -8); do
    test_example "$example"
done

# Priority 4: Test selected use-cases (sample)
print_status "Priority 4: Testing sample use-case examples"
echo "" >> ../../comprehensive_test_results.md
echo "## 💼 Priority 4: Sample Use Cases" >> ../../comprehensive_test_results.md
echo "" >> ../../comprehensive_test_results.md

# Test a few representative use-case examples
for example in $(find use-cases -name "*.py" -type f 2>/dev/null | grep -v __init__ | grep -v _utils | head -5); do
    test_example "$example"
done

# Priority 5: Test selected integration examples  
print_status "Priority 5: Testing sample integration examples"
echo "" >> ../../comprehensive_test_results.md
echo "## 🔌 Priority 5: Sample Integrations" >> ../../comprehensive_test_results.md
echo "" >> ../../comprehensive_test_results.md

# Test a few integration examples (avoiding complex ones that need special setup)
for example in $(find integrations -name "*.py" -type f 2>/dev/null | grep -v __init__ | grep -v _utils | head -3); do
    # Skip langchain main.py as it's complex
    if [[ "$example" != *"langchain/main.py"* ]]; then
        test_example "$example"
    fi
done

# Generate final statistics
echo "" >> ../../comprehensive_test_results.md
echo "## 📊 Final Test Statistics" >> ../../comprehensive_test_results.md
echo "" >> ../../comprehensive_test_results.md
echo "- **Total Tested**: $TOTAL_TESTED examples" >> ../../comprehensive_test_results.md
echo "- **✅ Successful**: $SUCCESSFUL_TESTS examples" >> ../../comprehensive_test_results.md
echo "- **❌ Failed**: $FAILED_TESTS examples" >> ../../comprehensive_test_results.md
echo "- **⏭️ Skipped**: $SKIPPED_TESTS examples (utility files)" >> ../../comprehensive_test_results.md
echo "" >> ../../comprehensive_test_results.md

# Calculate success rate
if [ $TOTAL_TESTED -gt 0 ]; then
    SUCCESS_RATE=$(( (SUCCESSFUL_TESTS * 100) / TOTAL_TESTED ))
    echo "- **Success Rate**: ${SUCCESS_RATE}%" >> ../../comprehensive_test_results.md
fi

echo "" >> ../../comprehensive_test_results.md
echo "## 📝 Log Files" >> ../../comprehensive_test_results.md
echo "" >> ../../comprehensive_test_results.md
echo "Individual test logs available in current directory:" >> ../../comprehensive_test_results.md
echo "\`\`\`" >> ../../comprehensive_test_results.md
cd ../../
ls test_*.log 2>/dev/null | head -10 >> comprehensive_test_results.md
echo "\`\`\`" >> comprehensive_test_results.md

print_success "Comprehensive testing completed!"
print_status "Results: $SUCCESSFUL_TESTS successful, $FAILED_TESTS failed, $SKIPPED_TESTS skipped out of $TOTAL_TESTED tested"

# 10. Generate validation report
print_status "Step 10: Generating validation report"
cd "../../.."

cat > validation_report.md << EOF
# TraiGent SDK Validation Report

**Date**: $(date)
**Environment**: Fresh virtual environment
**Installation Method**: \`pip install "git+${REPO_URL}#egg=traigent[examples]"\`

## Test Results Summary

### ✅ Successful Tests
$([ $HELLO_RESULT -eq 0 ] && echo "- hello_traigent.py example" || echo "")
$([ $BASIC_RESULT -eq 0 ] && echo "- basic_optimization.py example" || echo "")
- Dependency imports (traigent, langchain-openai, anthropic, dotenv)
- Virtual environment setup
- SDK installation from GitHub

### ⚠️ Issues Detected
$([ $HELLO_RESULT -ne 0 ] && echo "- hello_traigent.py execution failed" || echo "")
$([ $BASIC_RESULT -ne 0 ] && echo "- basic_optimization.py execution failed" || echo "")

### 📊 Optimization Results
$(cd "$TEST_DIR/traigent_repo/examples" && grep "Best configuration:" basic_test.log 2>/dev/null || echo "No optimization results found")
$(cd "$TEST_DIR/traigent_repo/examples" && grep "Best accuracy:" basic_test.log 2>/dev/null || echo "No accuracy results found")

### 📝 Log Files
- Full logs available in: \`${TEST_DIR}/traigent_repo/examples/\`
  - hello_test.log
  - basic_test.log
  - install.log
  - clone.log

## New User Experience Assessment

**Overall Status**: $([ $HELLO_RESULT -eq 0 ] && [ $BASIC_RESULT -eq 0 ] && echo "✅ EXCELLENT - New users can successfully install and run examples" || echo "⚠️ NEEDS ATTENTION - Some examples failed")

**Installation Experience**: ✅ Smooth - Single command installs all dependencies
**Example Execution**: $([ $HELLO_RESULT -eq 0 ] && [ $BASIC_RESULT -eq 0 ] && echo "✅ Working" || echo "⚠️ Has issues")
**Comprehensive Testing**: ${SUCCESSFUL_TESTS}/${TOTAL_TESTED} examples successful ($([ $TOTAL_TESTED -gt 0 ] && echo $(( (SUCCESSFUL_TESTS * 100) / TOTAL_TESTED )) || echo "0")% success rate)
**Documentation Clarity**: Requires testing with actual new users

## Comprehensive Testing Results

- **Total Examples Tested**: ${TOTAL_TESTED}
- **Successful**: ${SUCCESSFUL_TESTS} examples  
- **Failed**: ${FAILED_TESTS} examples
- **Skipped**: ${SKIPPED_TESTS} examples (utility files)
- **Success Rate**: $([ $TOTAL_TESTED -gt 0 ] && echo $(( (SUCCESSFUL_TESTS * 100) / TOTAL_TESTED )) || echo "0")%

**Detailed Results**: See \`comprehensive_test_results.md\` for full test breakdown

## Recommendations

1. **For SDK Team**: $([ $HELLO_RESULT -eq 0 ] && [ $BASIC_RESULT -eq 0 ] && echo "Great work! Core examples run successfully." || echo "Check failed examples and fix import/execution issues.")
   - $([ $SUCCESSFUL_TESTS -gt $(( TOTAL_TESTED / 2 )) ] && echo "Most comprehensive examples working" || echo "Many examples need attention - check comprehensive_test_results.md")

2. **For Documentation**: Update README with exact installation command tested here

3. **Next Steps**: 
   - Review failed examples in comprehensive_test_results.md
   - Fix import/dependency issues for failing examples
   - Test with actual new users to validate documentation clarity
EOF

print_success "Validation report generated: validation_report.md"

# 10. Summary
echo ""
echo "🎯 VALIDATION SUMMARY"
echo "===================="
print_status "Virtual Environment: ✅ Created successfully"
print_status "SDK Installation: ✅ Completed successfully"
print_status "Dependency Imports: ✅ All working"

if [ $HELLO_RESULT -eq 0 ]; then
    print_success "hello_traigent.py: ✅ Working"
else
    print_error "hello_traigent.py: ❌ Failed"
fi

if [ $BASIC_RESULT -eq 0 ]; then
    print_success "basic_optimization.py: ✅ Working"
else
    print_error "basic_optimization.py: ❌ Failed"
fi

echo ""
print_status "📊 COMPREHENSIVE TEST SUMMARY:"
echo "   Core Examples: $([ $HELLO_RESULT -eq 0 ] && [ $BASIC_RESULT -eq 0 ] && echo "✅ Working" || echo "❌ Failed")"
echo "   Comprehensive: ${SUCCESSFUL_TESTS}/${TOTAL_TESTED} examples successful"
echo "   Success Rate: $([ $TOTAL_TESTED -gt 0 ] && echo $(( (SUCCESSFUL_TESTS * 100) / TOTAL_TESTED )) || echo "0")%"

echo ""
if [ $HELLO_RESULT -eq 0 ] && [ $BASIC_RESULT -eq 0 ] && [ $SUCCESSFUL_TESTS -gt $(( TOTAL_TESTED / 2 )) ]; then
    print_success "🎉 COMPREHENSIVE VALIDATION PASSED - SDK ready for new users!"
    print_status "📋 Review comprehensive_test_results.md for detailed breakdown"
    exit 0
elif [ $HELLO_RESULT -eq 0 ] && [ $BASIC_RESULT -eq 0 ]; then
    print_warning "⚠️ CORE EXAMPLES WORK but many comprehensive examples failed"
    print_status "✅ SDK suitable for basic use, but comprehensive examples need attention"
    print_status "📋 Check comprehensive_test_results.md and logs for failing examples"
    exit 0
else
    print_error "❌ CORE TESTS FAILED - SDK needs immediate attention"
    echo ""
    print_status "Check the logs in ${TEST_DIR}/traigent_repo/examples/ for details"
    exit 1
fi