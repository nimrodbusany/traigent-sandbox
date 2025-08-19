# How to Run TraiGent Benchmark CLI

## Main Script

```bash
python traigent_benchmark_cli.py
```

The main CLI now includes ALL fixes integrated:
- ✅ **Auth Fix**: Automatically adds Authorization headers with your TRAIGENT_API_KEY
- ✅ **max_trials Fix**: Ensures max_trials is never None (defaults to 50)
- ✅ **Mock Mode**: Prevents real API calls
- ✅ **Connector Fix**: Handles SessionCreationRequest errors

## Usage Methods

### Method 1: Generate Commands with Web Interface

1. **Open the command generator**:
   ```bash
   # Open in your browser
   firefox cli_generator.html
   # Or just double-click the HTML file
   ```

2. **Select your parameters** using the checkboxes

3. **Copy and run the generated command** directly:
   ```bash
   echo 'model=["gpt-3.5-turbo","gpt-4o-mini"] temperature=[0.3,0.7]' | python traigent_benchmark_cli.py
   ```

### Method 2: Interactive Mode

Run the CLI interactively and follow the guided wizard:
```bash
python traigent_benchmark_cli.py
```

Then choose option 2 (Guided Configuration) and follow the prompts.

### Method 3: Direct Commands

#### Quick 2-parameter test (4 combinations):
```bash
echo 'model=["gpt-3.5-turbo","gpt-4o-mini"] temperature=[0.3,0.7]' | python traigent_benchmark_cli.py
```

#### Medium 3-parameter test (18 combinations):
```bash
echo 'model=["gpt-3.5-turbo","gpt-4o-mini","gpt-4o"] temperature=[0.3,0.7,0.9] max_tokens=[50,100]' | python traigent_benchmark_cli.py
```

#### Large 4-parameter test (36 combinations):
```bash
echo 'model=["gpt-3.5-turbo","gpt-4o-mini","gpt-4o"] temperature=[0.3,0.7] max_tokens=[50,100] top_p=[0.5,0.9,1.0]' | python traigent_benchmark_cli.py
```

## What the Fixes Do

### Fix 1: Authorization Headers
The SDK has a bug where it doesn't include Authorization headers in many HTTP requests. Our fix intercepts all requests to the backend and adds the header automatically.

### Fix 2: max_trials Auto-Completion
The SDK sends `null` for max_trials which crashes the backend. Our fix:
- Sets a default of 50 if max_trials is not specified
- Ensures max_trials is never None in any request

## Environment Variables Required

Make sure these are set (they should already be in your `.env` file):
```bash
TRAIGENT_API_KEY=sk_n_8mXqLXt-eIpWeBpcOfoE8gfq44f1TMGYats_rQ-P4
TRAIGENT_BACKEND_URL=http://localhost:5000
TRAIGENT_EXECUTION_MODE=local
TRAIGENT_MOCK_MODE=true
```

## Notes

- **All fixes are now integrated into `traigent_benchmark_cli.py`**
- The fixes are applied automatically at startup
- You don't need to specify max_trials - it will default to 50 if not provided
- Mock mode is enabled by default to avoid API costs during testing