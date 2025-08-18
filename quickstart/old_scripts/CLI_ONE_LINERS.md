# TraiGent CLI One-Liner Commands

Complete commands that inline all responses - just copy and paste!

## 🚀 Quick Test (5 examples, 2 parameters)

### Using echo with pipe
```bash
source cli_venv/bin/activate && echo -e "2\nquick_test\n5\n1\n2\n2\n1\n0\ny\ny\nn\n2\ny\nn\n2\nn\nn\nn\nn\nn\nn\n1\ny\nn\ny\ny\ny" | python traigent_benchmark_cli.py
```

### Using heredoc (cleaner)
```bash
source cli_venv/bin/activate && python traigent_benchmark_cli.py << EOF
2
quick_test
5
1
2
2
1
0
y
y
n
2
y
n
2
n
n
n
n
n
n
1
y
n
y
y
y
EOF
```

### Using the run script
```bash
source cli_venv/bin/activate && ./run_quick_test.sh
```

### Using Python runner
```bash
source cli_venv/bin/activate && python run_with_config.py quick
```

## 📊 Basic Test (10 examples, 3 parameters)

### Using echo with pipe
```bash
source cli_venv/bin/activate && echo -e "2\nbasic_test\n10\n1\n3\n3\n2\n2\ny\ny\nn\n2\ny\nn\n2\ny\nn\n2\nn\nn\nn\nn\nn\n1\ny\nn\ny\ny\ny" | python traigent_benchmark_cli.py
```

### Using heredoc
```bash
source cli_venv/bin/activate && python traigent_benchmark_cli.py << EOF
2
basic_test
10
1
3
3
2
2
y
y
n
2
y
n
2
y
n
2
n
n
n
n
n
1
y
n
y
y
y
EOF
```

### Using the run script
```bash
source cli_venv/bin/activate && ./run_basic_test.sh
```

### Using Python runner
```bash
source cli_venv/bin/activate && python run_with_config.py basic
```

## 🔬 Advanced Test (15 examples, 5+ parameters)

### Using echo with pipe (long)
```bash
source cli_venv/bin/activate && echo -e "2\nadvanced_test\n15\n1\n4\n4\n4\n3\ny\ny\nn\n2\ny\nn\n3\nn\nn\ny\ny\nn\n2\ny\nn\n2\ny\ny\nn\n2\ny\nn\n2\nn\nn\nn\n1\ny\nn\ny\ny\ny" | python traigent_benchmark_cli.py
```

### Using heredoc (recommended for complex)
```bash
source cli_venv/bin/activate && python traigent_benchmark_cli.py << 'EOF'
2
advanced_test
15
1
4
4
4
3
y
y
n
2
y
n
3
n
n
y
y
n
2
y
n
2
y
y
n
2
y
n
2
n
n
n
1
y
n
y
y
y
EOF
```

### Using the run script
```bash
source cli_venv/bin/activate && ./run_advanced_test.sh
```

### Using Python runner
```bash
source cli_venv/bin/activate && python run_with_config.py advanced
```

## 🎯 Custom Configuration Examples

### Minimal (1 param, 3 examples)
```bash
source cli_venv/bin/activate && python traigent_benchmark_cli.py << EOF
2
minimal_test
3
3
y
y
n
1
n
n
n
n
n
n
1
y
n
y
n
n
EOF
```

### Model-only test
```bash
source cli_venv/bin/activate && printf '%s\n' 2 model_test 5 3 y y n 3 n n n n n n 1 y n y y n | python traigent_benchmark_cli.py
```

### Few-shot learning focus
```bash
source cli_venv/bin/activate && python traigent_benchmark_cli.py << EOF
2
fewshot_test
8
1
2
2
2
2
y
y
n
1
y
n
2
n
n
y
y
n
3
y
n
2
n
n
n
1
y
n
y
y
y
EOF
```

## 🛠️ Utility One-Liners

### View saved configurations
```bash
ls -la benchmark_configs/*.yaml
```

### Show dataset statistics
```bash
python -c "import json; d=json.load(open('support_classification_dataset.json')); print(f'Examples: {len(d[\"examples\"])}, Categories: {d[\"metadata\"][\"categories\"]}')"
```

### Test environment setup
```bash
source cli_venv/bin/activate && python -c "import traigent, openai, pandas; print('✅ All dependencies OK')"
```

### Clean up temp files
```bash
rm -f temp_input.txt test_input.txt /tmp/tmp*.jsonl
```

### Run with saved config input
```bash
source cli_venv/bin/activate && cat test_input.txt | python traigent_benchmark_cli.py
```

## 💡 Tips for Creating Your Own One-Liners

### Understanding the input sequence:
1. Configuration mode (2 = Guided)
2. Experiment name
3. Number of examples
4. Sampling strategy (1=stratified, 2=random, 3=sequential)
5. Difficulty distribution (4 numbers if stratified)
6. Parameter selections (y/n for categories, then y/n and count for each param)
7. Execution mode (1=local, 2=standard, 3=cloud)
8. Mock mode (y/n)
9. Early stopping (y/n)
10. Proceed (y/n)
11. Save config (y/n)
12. Run now (y/n)

### Using printf for better control:
```bash
printf '%s\n' value1 value2 value3 | python traigent_benchmark_cli.py
```

### Using a file for complex inputs:
```bash
cat > my_config.txt << EOF
2
my_test
10
1
3
3
2
2
y
...
EOF
cat my_config.txt | python traigent_benchmark_cli.py
```

### Combining with other tools:
```bash
# Run and save output
source cli_venv/bin/activate && python run_with_config.py quick 2>&1 | tee output.log

# Run and extract specific info
source cli_venv/bin/activate && python run_with_config.py basic | grep "Best config"

# Run multiple configs in sequence
for config in quick basic advanced; do
    echo "Running $config..."
    python run_with_config.py $config
    sleep 2
done
```