#!/bin/bash
# Test the improved CLI with guided configuration
echo -e "2\noptimization_test\n10\n3\ny\ny\ny\ngpt-3.5-turbo,gpt-4o-mini\ny\ny\n0.0,0.5,1.0\nn\nn\nn\nn\nn\n1\ny\nn\ny\ny\ny" | python traigent_benchmark_cli.py