#!/usr/bin/env python3

#Simple test runner for AI functions


import sys
import os
sys.path.append(".")

from test_ai_functions import run_tests

if __name__ == "__main__":
    print("Starting AI Functions Test Suite...")
    success = run_tests()
    
    if success:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")
    
    sys.exit(0 if success else 1)
