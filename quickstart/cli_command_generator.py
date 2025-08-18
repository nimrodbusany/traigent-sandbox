#!/usr/bin/env python3
"""
TraiGent CLI Command Generator Web App
Generate copy-paste commands for the TraiGent benchmark CLI
"""

import streamlit as st
import json

st.set_page_config(
    page_title="TraiGent CLI Command Generator",
    page_icon="🎯",
    layout="wide"
)

# Title and description
st.title("🎯 TraiGent CLI Command Generator")
st.markdown("""
Generate copy-paste commands for the TraiGent benchmark CLI with your desired parameters.
Configure your optimization experiment below and get a ready-to-run command.
""")

# Create two columns
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 Configuration")
    
    # Basic Configuration
    st.subheader("Basic Settings")
    experiment_name = st.text_input("Experiment Name", value="optimization_test")
    num_examples = st.slider("Number of Examples", min_value=3, max_value=30, value=10)
    sampling_strategy = st.selectbox(
        "Sampling Strategy",
        options=["stratified", "random", "sequential"],
        format_func=lambda x: {
            "stratified": "1. Stratified (balanced)",
            "random": "2. Random sampling", 
            "sequential": "3. Sequential (first N)"
        }[x]
    )
    
    # Parameter Configuration
    st.subheader("🔧 Parameter Space")
    
    # Model selection
    st.markdown("**Model Selection**")
    model_options = ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o", "gpt-4"]
    selected_models = st.multiselect(
        "Select Models to Test",
        options=model_options,
        default=["gpt-3.5-turbo", "gpt-4o-mini"]
    )
    
    # Temperature selection
    st.markdown("**Temperature Values**")
    temp_options = [0.0, 0.3, 0.5, 0.7, 1.0]
    selected_temps = st.multiselect(
        "Select Temperature Values",
        options=temp_options,
        default=[0.0, 0.5, 1.0]
    )
    
    # Max tokens selection
    st.markdown("**Max Tokens**")
    include_max_tokens = st.checkbox("Include max_tokens parameter", value=False)
    if include_max_tokens:
        token_options = [10, 20, 50, 100, 200]
        selected_tokens = st.multiselect(
            "Select Max Token Values",
            options=token_options,
            default=[50, 100]
        )
    else:
        selected_tokens = []
    
    # Top-p selection
    st.markdown("**Top-p (Nucleus Sampling)**")
    include_top_p = st.checkbox("Include top_p parameter", value=False)
    if include_top_p:
        top_p_options = [0.1, 0.5, 0.9, 1.0]
        selected_top_p = st.multiselect(
            "Select Top-p Values",
            options=top_p_options,
            default=[0.5, 1.0]
        )
    else:
        selected_top_p = []
    
    # Few-shot learning
    st.markdown("**Few-Shot Learning**")
    include_few_shot = st.checkbox("Include few-shot parameters", value=False)
    if include_few_shot:
        few_shot_k_options = [0, 1, 3, 5, 8]
        selected_few_shot_k = st.multiselect(
            "Select Few-Shot K Values",
            options=few_shot_k_options,
            default=[0, 3]
        )
    else:
        selected_few_shot_k = []
    
    # Prompt Engineering
    st.markdown("**Prompt Engineering**")
    include_prompt_eng = st.checkbox("Include prompt engineering parameters", value=False)
    if include_prompt_eng:
        include_system_role = st.checkbox("Include system_role", value=True)
        include_chain_of_thought = st.checkbox("Include chain_of_thought", value=True)
    else:
        include_system_role = False
        include_chain_of_thought = False
    
    # Execution Configuration
    st.subheader("⚙️ Execution Settings")
    execution_mode = st.selectbox(
        "Execution Mode",
        options=["local", "standard", "cloud"],
        format_func=lambda x: {
            "local": "1. Local (no backend)",
            "standard": "2. Standard (hybrid)",
            "cloud": "3. Cloud (full cloud)"
        }[x]
    )
    mock_mode = st.checkbox("Use Mock Mode (no API costs)", value=True)
    early_stopping = st.checkbox("Enable Early Stopping", value=False)

with col2:
    st.header("📊 Summary")
    
    # Calculate total combinations
    total_combinations = len(selected_models) * len(selected_temps)
    if include_max_tokens and selected_tokens:
        total_combinations *= len(selected_tokens)
    if include_top_p and selected_top_p:
        total_combinations *= len(selected_top_p)
    if include_few_shot and selected_few_shot_k:
        total_combinations *= len(selected_few_shot_k)
    if include_prompt_eng:
        if include_system_role:
            total_combinations *= 2  # Two system roles
        if include_chain_of_thought:
            total_combinations *= 2  # True/False
    
    st.metric("Total Parameter Combinations", total_combinations)
    st.metric("Models", len(selected_models))
    st.metric("Temperature Values", len(selected_temps))
    
    if include_max_tokens:
        st.metric("Max Token Values", len(selected_tokens))
    if include_top_p:
        st.metric("Top-p Values", len(selected_top_p))
    if include_few_shot:
        st.metric("Few-Shot K Values", len(selected_few_shot_k))
    
    # Cost estimation (rough)
    if not mock_mode:
        estimated_cost = total_combinations * num_examples * 0.001  # Rough estimate
        st.warning(f"⚠️ Estimated cost: ${estimated_cost:.2f}")
    else:
        st.success("✅ Mock mode enabled (no costs)")

# Generate the command
st.header("🚀 Generated Command")

def generate_command():
    """Generate the CLI command based on current settings"""
    
    # Map sampling strategy to number
    strategy_map = {"stratified": "1", "random": "2", "sequential": "3"}
    strategy_num = strategy_map[sampling_strategy]
    
    # Map execution mode to number
    mode_map = {"local": "1", "standard": "2", "cloud": "3"}
    mode_num = mode_map[execution_mode]
    
    # Build the input sequence
    inputs = []
    inputs.append("2")  # Guided configuration
    inputs.append(experiment_name)
    inputs.append(str(num_examples))
    inputs.append(strategy_num)
    
    # Core LLM parameters
    inputs.append("y")  # Include Core LLM
    
    # Model
    inputs.append("y")  # Include model
    if len(selected_models) == len(model_options):
        inputs.append("n")  # Use default values
        inputs.append(str(len(selected_models)))
    else:
        inputs.append("y")  # Use custom values
        inputs.append(",".join(selected_models))
    
    # Temperature
    inputs.append("y")  # Include temperature
    if set(selected_temps) == set(temp_options[:len(selected_temps)]):
        inputs.append("n")  # Use default values
        inputs.append(str(len(selected_temps)))
    else:
        inputs.append("y")  # Use custom values
        inputs.append(",".join(map(str, selected_temps)))
    
    # Max tokens
    if include_max_tokens:
        inputs.append("y")  # Include max_tokens
        inputs.append("n")  # Use default values (simplified)
        inputs.append(str(len(selected_tokens)))
    else:
        inputs.append("n")  # Skip max_tokens
    
    # Top-p
    if include_top_p:
        inputs.append("y")  # Include top_p
        inputs.append("n")  # Use default values (simplified)
        inputs.append(str(len(selected_top_p)))
    else:
        inputs.append("n")  # Skip top_p
    
    # Few-shot learning
    if include_few_shot:
        inputs.append("y")  # Include few-shot
        inputs.append("y")  # Include few_shot_k
        inputs.append("n")  # Use default values
        inputs.append(str(len(selected_few_shot_k)))
        inputs.append("n")  # Skip few_shot_strategy
    else:
        inputs.append("n")  # Skip few-shot
    
    # Prompt engineering
    if include_prompt_eng:
        inputs.append("y")  # Include prompt engineering
        if include_system_role:
            inputs.append("y")  # Include system_role
        else:
            inputs.append("n")
        if include_chain_of_thought:
            inputs.append("y")  # Include chain_of_thought
        else:
            inputs.append("n")
    else:
        inputs.append("n")  # Skip prompt engineering
    
    # Context/Retrieval
    inputs.append("n")  # Skip context/retrieval
    
    # Execution configuration
    inputs.append(mode_num)
    inputs.append("y" if mock_mode else "n")
    inputs.append("y" if early_stopping else "n")
    
    # Final confirmations
    inputs.append("y")  # Proceed
    inputs.append("y")  # Save config
    inputs.append("y")  # Run now
    
    return inputs

# Generate and display the command
inputs = generate_command()

# Create the echo command
inputs_str = '\\n'.join(inputs)
echo_command = f'echo -e "{inputs_str}" | python traigent_benchmark_cli.py'

# Create the heredoc command
heredoc_command = f"""python traigent_benchmark_cli.py << 'EOF'
{chr(10).join(inputs)}
EOF"""

# Display commands
tab1, tab2, tab3 = st.tabs(["Echo Command", "Heredoc Command", "Python Script"])

with tab1:
    st.code(f"""# Activate virtual environment and run
source cli_venv/bin/activate
{echo_command}""", language="bash")
    
    if st.button("📋 Copy Echo Command", key="copy_echo"):
        st.write("Command copied! (use browser's copy function)")

with tab2:
    st.code(f"""# Activate virtual environment and run
source cli_venv/bin/activate
{heredoc_command}""", language="bash")
    
    if st.button("📋 Copy Heredoc Command", key="copy_heredoc"):
        st.write("Command copied! (use browser's copy function)")

with tab3:
    python_script = f"""#!/usr/bin/env python3
# Generated TraiGent CLI configuration script

import subprocess
import sys

inputs = {json.dumps(inputs, indent=2)}

# Run the CLI with the inputs
process = subprocess.Popen(
    [sys.executable, 'traigent_benchmark_cli.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

output, _ = process.communicate(input='\\n'.join(inputs))
print(output)
"""
    
    st.code(python_script, language="python")
    
    if st.button("📋 Copy Python Script", key="copy_python"):
        st.write("Command copied! (use browser's copy function)")

# Configuration summary
with st.expander("📝 Configuration Details"):
    config = {
        "experiment_name": experiment_name,
        "num_examples": num_examples,
        "sampling_strategy": sampling_strategy,
        "parameters": {
            "models": selected_models,
            "temperatures": selected_temps,
            "max_tokens": selected_tokens if include_max_tokens else None,
            "top_p": selected_top_p if include_top_p else None,
            "few_shot_k": selected_few_shot_k if include_few_shot else None,
            "system_role": include_system_role,
            "chain_of_thought": include_chain_of_thought
        },
        "execution": {
            "mode": execution_mode,
            "mock_mode": mock_mode,
            "early_stopping": early_stopping
        },
        "total_combinations": total_combinations
    }
    st.json(config)

# Instructions
st.markdown("---")
st.markdown("""
### 📖 How to Use

1. **Configure your experiment** using the settings on the left
2. **Review the summary** on the right to see total parameter combinations
3. **Copy the generated command** from one of the tabs above
4. **Open your terminal** and navigate to the quickstart directory
5. **Paste and run** the command

### 🎯 Tips

- Start with **mock mode enabled** to test without API costs
- Use **3-4 parameters** for ~20 configurations (e.g., 3 models × 3 temps × 2 max_tokens = 18)
- The **heredoc command** is cleaner for complex configurations
- Save configurations for reuse by answering "y" to "Save this configuration?"
""")