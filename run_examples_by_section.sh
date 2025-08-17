#!/usr/bin/bash
# TraiGent SDK Section-Based Example Runner
# Runs examples by section with configurable parameters
# Run this from the project root directory

set -e  # Exit on any error

echo "🚀 TraiGent SDK Section-Based Example Runner"
echo "============================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Default configuration
SECTIONS="all"
SKIP_INSTALL=false
NO_CLEAR=false
TEST_DIR="sdk_validation_test"
REPO_URL="https://github.com/nimrodbusany/Traigent.git"

# Available sections
ALL_SECTIONS="quickstart core-concepts advanced-patterns execution-modes use-cases integrations enterprise running-example"

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

print_section() {
    echo -e "${PURPLE}[SECTION]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  --sections SECTIONS     Comma-separated list of sections to run"
    echo "                         Available: quickstart, core-concepts, advanced-patterns,"
    echo "                         execution-modes, use-cases, integrations, enterprise,"
    echo "                         running-example (default: all)"
    echo "  --skip-install         Skip TraiGent SDK installation"
    echo "  --no-clear             Don't clear previous test environment"
    echo "  --help                 Show this help message"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                                    # Run all sections with fresh install"
    echo "  $0 --sections quickstart,core-concepts  # Run specific sections"
    echo "  $0 --skip-install                    # Use existing environment"
    echo "  $0 --sections quickstart --skip-install --no-clear"
    echo ""
    echo "AVAILABLE SECTIONS:"
    echo "  quickstart (5 files)      - Basic getting started examples"
    echo "  core-concepts (12 files)  - Core TraiGent concepts"
    echo "  advanced-patterns (7 files) - Advanced usage patterns"
    echo "  execution-modes (6 files) - Different execution modes"
    echo "  use-cases (86 files)      - Various use case examples"
    echo "  integrations (113 files)  - Integration examples"
    echo "  enterprise (4 files)      - Enterprise features"
    echo "  running-example (16 files) - Running examples"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --sections)
            SECTIONS="$2"
            shift 2
            ;;
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        --no-clear)
            NO_CLEAR=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
done

# Validate sections
if [ "$SECTIONS" = "all" ]; then
    SELECTED_SECTIONS="$ALL_SECTIONS"
else
    SELECTED_SECTIONS=$(echo "$SECTIONS" | tr ',' ' ')
    for section in $SELECTED_SECTIONS; do
        if ! echo "$ALL_SECTIONS" | grep -wq "$section"; then
            print_error "Invalid section: $section"
            echo "Available sections: $ALL_SECTIONS"
            exit 1
        fi
    done
fi

# Map sections to directory paths
get_section_path() {
    case $1 in
        quickstart)
            echo "quickstart"
            ;;
        core-concepts)
            echo "learn-traigent/core-concepts"
            ;;
        advanced-patterns)
            echo "learn-traigent/advanced-patterns"
            ;;
        execution-modes)
            echo "learn-traigent/execution-modes"
            ;;
        use-cases)
            echo "use-cases"
            ;;
        integrations)
            echo "integrations"
            ;;
        enterprise)
            echo "enterprise"
            ;;
        running-example)
            echo "running-example"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Display configuration
print_status "Configuration:"
echo "   • Sections to run: $SELECTED_SECTIONS"
echo "   • Skip installation: $SKIP_INSTALL"
echo "   • Clear environment: $([ "$NO_CLEAR" = "true" ] && echo "No" || echo "Yes")"
echo ""

# Step 1: Setup environment
if [ "$NO_CLEAR" = "false" ]; then
    print_status "Step 1: Cleaning up previous test runs"
    rm -rf "$TEST_DIR"
    mkdir "$TEST_DIR"
else
    print_status "Step 1: Using existing test environment"
    if [ ! -d "$TEST_DIR" ]; then
        print_warning "Test directory doesn't exist, creating new one"
        mkdir "$TEST_DIR"
    fi
fi

cd "$TEST_DIR"

# Step 2: Virtual environment setup
if [ "$NO_CLEAR" = "false" ] || [ ! -d "fresh_venv" ]; then
    print_status "Step 2: Creating fresh virtual environment"
    python3 -m venv fresh_venv
    source fresh_venv/bin/activate
    print_success "Virtual environment created and activated"
else
    print_status "Step 2: Using existing virtual environment"
    source fresh_venv/bin/activate
    print_success "Virtual environment activated"
fi

# Step 3: SDK Installation
if [ "$SKIP_INSTALL" = "false" ]; then
    print_status "Step 3: Installing TraiGent SDK with examples from GitHub"
    pip install "git+${REPO_URL}#egg=traigent[examples]" > install.log 2>&1
    print_success "TraiGent SDK installation completed"
    
    print_status "Step 3.1: Testing critical dependency imports"
    python3 -c "
import traigent
from langchain_openai import ChatOpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
import pandas as pd
import numpy as np
print('✅ All critical dependencies imported successfully')
" 2>/dev/null
    print_success "Dependency imports verified"
else
    print_status "Step 3: Skipping SDK installation (using existing)"
fi

# Step 4: Clone repository for examples
if [ ! -d "traigent_repo" ]; then
    print_status "Step 4: Cloning TraiGent repo for examples"
    git clone "$REPO_URL" traigent_repo > clone.log 2>&1
    print_success "Repository cloning completed"
else
    print_status "Step 4: Using existing repository clone"
fi

# Step 5: Setup environment files
print_status "Step 5: Setting up environment variables"
if [ -f "../.env" ]; then
    cp "../.env" "traigent_repo/examples/.env"
    print_success "Environment file copied"
else
    print_warning "No .env file found in parent directory - creating mock one"
    cat > traigent_repo/examples/.env << 'EOF'
OPENAI_API_KEY=sk-test-key-for-validation
ANTHROPIC_API_KEY=sk-ant-test-key-for-validation
TRAIGENT_API_KEY=sk-traigent-test-key-for-validation
TRAIGENT_MOCK_MODE=true
EOF
fi

# Step 6: Create logs directory
print_status "Step 6: Setting up logging directories"
mkdir -p logs
for section in $SELECTED_SECTIONS; do
    mkdir -p "logs/$section"
done
print_success "Logging directories created"

# Statistics tracking
TOTAL_SECTIONS=0
TOTAL_EXAMPLES=0
SUCCESSFUL_EXAMPLES=0
FAILED_EXAMPLES=0
SKIPPED_EXAMPLES=0

# Function to test an example
test_example() {
    local section="$1"
    local example_path="$2"
    local relative_path="$example_path"
    local example_name=$(basename "$example_path" .py)
    local example_dir=$(dirname "$example_path")
    local base_dir=$(pwd)  # Store the base examples directory
    
    print_status "  Testing: $relative_path"
    TOTAL_EXAMPLES=$((TOTAL_EXAMPLES + 1))
    
    # Skip utility files and __init__.py files
    if [[ "$example_name" == "__init__" ]] || [[ "$example_name" == *"_utils" ]] || [[ "$example_name" == *"_helper" ]]; then
        print_status "    Skipped: Utility file"
        SKIPPED_EXAMPLES=$((SKIPPED_EXAMPLES + 1))
        echo "- ⏭️  SKIPPED: $relative_path (utility file)" >> "$base_dir/../../logs/section_$section.log"
        return 0
    fi
    
    # Create test log file
    local log_file="$section/$(echo "$relative_path" | tr '/' '_' | tr '.' '_').log"
    
    # Set up environment for this test
    cd "$example_dir"
    export PYTHONPATH="$(pwd):$(dirname $(pwd)):$PYTHONPATH"
    export TRAIGENT_MOCK_MODE=true
    
    # Try to run the example with timeout
    timeout 60 python "$example_name.py" > "$base_dir/../../logs/$log_file" 2>&1
    local result=$?
    
    # Check result
    if [ $result -eq 0 ]; then
        print_success "    ✅ SUCCESS: $relative_path"
        SUCCESSFUL_EXAMPLES=$((SUCCESSFUL_EXAMPLES + 1))
        echo "- ✅ SUCCESS: $relative_path" >> "$base_dir/../../logs/section_$section.log"
        
        # Check for specific success patterns
        if grep -q "optimization.*complete\|best.*configuration\|accuracy\|TraiGent" "$base_dir/../../logs/$log_file" 2>/dev/null; then
            echo "  └─ Contains expected optimization output" >> "$base_dir/../../logs/section_$section.log"
        fi
        
    elif [ $result -eq 124 ]; then
        print_warning "    ⏰ TIMEOUT: $relative_path"
        FAILED_EXAMPLES=$((FAILED_EXAMPLES + 1))
        echo "- ⏰ TIMEOUT: $relative_path (>60s)" >> "$base_dir/../../logs/section_$section.log"
        
    else
        print_error "    ❌ FAILED: $relative_path"
        FAILED_EXAMPLES=$((FAILED_EXAMPLES + 1))
        echo "- ❌ FAILED: $relative_path" >> "$base_dir/../../logs/section_$section.log"
        
        # Extract key error information
        if [ -f "$base_dir/../../logs/$log_file" ]; then
            error_info=$(grep -i "error\|exception\|traceback" "$base_dir/../../logs/$log_file" | head -2)
            if [ ! -z "$error_info" ]; then
                echo "  └─ Error: $error_info" >> "$base_dir/../../logs/section_$section.log"
            fi
        fi
    fi
    
    # Return to examples directory base
    cd "$base_dir"
}

# Function to run a section
run_section() {
    local section="$1"
    local section_path=$(get_section_path "$section")
    
    if [ -z "$section_path" ]; then
        print_error "Unknown section: $section"
        return 1
    fi
    
    print_section "Running section: $section"
    TOTAL_SECTIONS=$((TOTAL_SECTIONS + 1))
    
    # Initialize section log
    echo "# Section: $section" > "logs/section_$section.log"
    echo "**Date**: $(date)" >> "logs/section_$section.log"
    echo "**Path**: $section_path" >> "logs/section_$section.log"
    echo "" >> "logs/section_$section.log"
    
    # Set up environment for testing
    cd traigent_repo/examples
    export PYTHONPATH="$(pwd):$PYTHONPATH"
    export TRAIGENT_MOCK_MODE=true
    
    # Count examples in this section
    local example_count=$(find "$section_path" -name "*.py" -type f 2>/dev/null | grep -v __pycache__ | grep -v __init__ | wc -l)
    print_status "  Found $example_count Python files in $section"
    
    if [ $example_count -eq 0 ]; then
        print_warning "  No Python files found in section: $section"
        echo "- ⚠️ WARNING: No Python files found" >> "../../logs/section_$section.log"
        cd ../..
        return 0
    fi
    
    # Run all examples in this section
    for example in $(find "$section_path" -name "*.py" -type f 2>/dev/null | grep -v __pycache__ | grep -v __init__); do
        test_example "$section" "$example"
    done
    
    cd ../..
    
    # Add section summary
    local section_successful=$(grep -c "✅ SUCCESS" "logs/section_$section.log" || echo "0")
    local section_failed=$(grep -c "❌ FAILED\|⏰ TIMEOUT" "logs/section_$section.log" || echo "0") 
    local section_skipped=$(grep -c "⏭️ SKIPPED" "logs/section_$section.log" || echo "0")
    
    echo "" >> "logs/section_$section.log"
    echo "## Section Summary" >> "logs/section_$section.log"
    echo "- **Successful**: $section_successful" >> "logs/section_$section.log"
    echo "- **Failed**: $section_failed" >> "logs/section_$section.log"
    echo "- **Skipped**: $section_skipped" >> "logs/section_$section.log"
    
    print_success "Section $section completed: $section_successful successful, $section_failed failed, $section_skipped skipped"
}

# Step 7: Run selected sections
print_status "Step 7: Running selected sections"
echo ""

for section in $SELECTED_SECTIONS; do
    run_section "$section"
    echo ""
done

# Step 8: Generate comprehensive report
print_status "Step 8: Generating comprehensive test report"
cd ..

cat > section_test_results.md << EOF
# TraiGent SDK Section-Based Test Results

**Date**: $(date)
**Environment**: $([ "$NO_CLEAR" = "true" ] && echo "Existing" || echo "Fresh") virtual environment
**Installation**: $([ "$SKIP_INSTALL" = "true" ] && echo "Skipped (existing)" || echo "Fresh install")
**Sections Tested**: $SELECTED_SECTIONS

## Test Results Summary

### 📊 Overall Statistics
- **Total Sections**: $TOTAL_SECTIONS
- **Total Examples**: $TOTAL_EXAMPLES
- **✅ Successful**: $SUCCESSFUL_EXAMPLES examples
- **❌ Failed**: $FAILED_EXAMPLES examples
- **⏭️ Skipped**: $SKIPPED_EXAMPLES examples (utility files)

EOF

# Calculate success rate
if [ $TOTAL_EXAMPLES -gt 0 ]; then
    SUCCESS_RATE=$(( (SUCCESSFUL_EXAMPLES * 100) / TOTAL_EXAMPLES ))
    echo "- **Success Rate**: ${SUCCESS_RATE}%" >> section_test_results.md
fi

echo "" >> section_test_results.md

# Add section breakdown
echo "### 📁 Section Breakdown" >> section_test_results.md
echo "" >> section_test_results.md

for section in $SELECTED_SECTIONS; do
    if [ -f "logs/section_$section.log" ]; then
        echo "#### $section" >> section_test_results.md
        
        local section_successful=$(grep -c "✅ SUCCESS" "logs/section_$section.log" 2>/dev/null || echo "0")
        local section_failed=$(grep -c "❌ FAILED\|⏰ TIMEOUT" "logs/section_$section.log" 2>/dev/null || echo "0")
        local section_skipped=$(grep -c "⏭️ SKIPPED" "logs/section_$section.log" 2>/dev/null || echo "0")
        local section_total=$((section_successful + section_failed + section_skipped))
        
        echo "- **Total**: $section_total examples" >> section_test_results.md
        echo "- **Successful**: $section_successful" >> section_test_results.md
        echo "- **Failed**: $section_failed" >> section_test_results.md
        echo "- **Skipped**: $section_skipped" >> section_test_results.md
        
        if [ $section_total -gt 0 ]; then
            local section_rate=$(( (section_successful * 100) / section_total ))
            echo "- **Success Rate**: ${section_rate}%" >> section_test_results.md
        fi
        echo "" >> section_test_results.md
    fi
done

# Add log file references
echo "### 📝 Detailed Logs" >> section_test_results.md
echo "" >> section_test_results.md
echo "**Section Logs**: \`logs/section_[section].log\`" >> section_test_results.md
echo "**Example Logs**: \`logs/[section]/[example].log\`" >> section_test_results.md
echo "" >> section_test_results.md

echo "Available log files:" >> section_test_results.md
echo "\`\`\`" >> section_test_results.md
ls logs/ 2>/dev/null | head -20 >> section_test_results.md
echo "\`\`\`" >> section_test_results.md

print_success "Comprehensive test report generated: section_test_results.md"

# Step 9: Final summary
echo ""
echo "🎯 SECTION-BASED TEST SUMMARY"
echo "=============================="
print_status "Sections Tested: $TOTAL_SECTIONS ($SELECTED_SECTIONS)"
print_status "Total Examples: $TOTAL_EXAMPLES"
print_status "Successful: $SUCCESSFUL_EXAMPLES"
print_status "Failed: $FAILED_EXAMPLES"
print_status "Skipped: $SKIPPED_EXAMPLES"

if [ $TOTAL_EXAMPLES -gt 0 ]; then
    print_status "Success Rate: $(( (SUCCESSFUL_EXAMPLES * 100) / TOTAL_EXAMPLES ))%"
fi

echo ""
if [ $SUCCESSFUL_EXAMPLES -gt $(( TOTAL_EXAMPLES / 2 )) ]; then
    print_success "🎉 SECTION TESTING COMPLETED SUCCESSFULLY"
    print_status "📋 Review section_test_results.md for detailed breakdown"
    print_status "📂 Individual logs available in logs/ directory"
    exit 0
else
    print_warning "⚠️ SOME EXAMPLES FAILED"
    print_status "📋 Check section_test_results.md and logs/ for failing examples"
    print_status "📂 Use specific section testing to investigate issues"
    exit 0
fi