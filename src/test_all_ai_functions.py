#!/usr/bin/env python3

#Comprehensive test runner for all AI functions
#Tests SearchNode, utility function, and bestMove function
##Unit test helped by ChatGPT

import unittest
import sys
import os
sys.path.append(".")

from test_ai_functions import (
    TestSearchNode, 
    TestUtilityFunction, 
    TestBestMoveFunction, 
    TestAIPlayerIntegration
)
from test_utility import TestUtilityFunctionFocused
from test_search_node import TestSearchNodeComprehensive

def run_all_tests():
    #Run all AI function tests with comprehensive reporting.
    print("=" * 80)
    print("COMPREHENSIVE AI FUNCTIONS TEST SUITE")
    print("=" * 80)
    print("Testing: SearchNode, Utility Function, and BestMove Function")
    print("=" * 80)
    
    # Create comprehensive test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_suite.addTest(unittest.makeSuite(TestSearchNode))
    test_suite.addTest(unittest.makeSuite(TestUtilityFunction))
    test_suite.addTest(unittest.makeSuite(TestBestMoveFunction))
    test_suite.addTest(unittest.makeSuite(TestAIPlayerIntegration))
    test_suite.addTest(unittest.makeSuite(TestUtilityFunctionFocused))
    test_suite.addTest(unittest.makeSuite(TestSearchNodeComprehensive))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(test_suite)
    
    # Print detailed summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n" + "=" * 40)
        print("FAILURES:")
        print("=" * 40)
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.split('AssertionError:')[-1].strip()}")
            print()
    
    if result.errors:
        print("\n" + "=" * 40)
        print("ERRORS:")
        print("=" * 40)
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.split('Exception:')[-1].strip()}")
            print()
    
    # Test coverage summary
    print("\n" + "=" * 40)
    print("TEST COVERAGE SUMMARY")
    print("=" * 40)
    print("✓ SearchNode Class:")
    print("  - Initialization and properties")
    print("  - Evaluation calculation")
    print("  - Parent-child relationships")
    print("  - Dictionary and string representations")
    print("  - Helper method integration")
    print()
    print("✓ Utility Function:")
    print("  - Basic functionality and constraints")
    print("  - Food scoring mechanisms")
    print("  - Queen status handling")
    print("  - Ant count and attacker scoring")
    print("  - Worker carrying food behavior")
    print("  - Edge cases and consistency")
    print()
    print("✓ BestMove Function:")
    print("  - Empty list handling")
    print("  - Single node selection")
    print("  - Multiple node comparison")
    print("  - Tie-breaking behavior")
    print("  - Different depth handling")
    print()
    print("✓ Integration Tests:")
    print("  - AIPlayer helper methods")
    print("  - End-to-end functionality")
    print("  - Edge case handling")
    
    return result.wasSuccessful()

def run_quick_tests():
    #Run a quick subset of tests for rapid feedback.
    print("=" * 60)
    print("QUICK AI FUNCTIONS TEST")
    print("=" * 60)
    
    # Create minimal test suite
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestSearchNode))
    test_suite.addTest(unittest.makeSuite(TestUtilityFunction))
    test_suite.addTest(unittest.makeSuite(TestBestMoveFunction))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(test_suite)
    
    print(f"\nQuick Test Results: {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")
    return result.wasSuccessful()

def run_function_specific_tests():
    #Run tests for specific functions based on user choice.
    print("=" * 60)
    print("FUNCTION-SPECIFIC TESTS")
    print("=" * 60)
    print("1. SearchNode only")
    print("2. Utility function only") 
    print("3. BestMove function only")
    print("4. All functions")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        test_suite = unittest.TestSuite()
        
        if choice == "1":
            test_suite.addTest(unittest.makeSuite(TestSearchNodeComprehensive))
            print("\nRunning SearchNode tests...")
        elif choice == "2":
            test_suite.addTest(unittest.makeSuite(TestUtilityFunctionFocused))
            print("\nRunning Utility function tests...")
        elif choice == "3":
            test_suite.addTest(unittest.makeSuite(TestBestMoveFunction))
            print("\nRunning BestMove function tests...")
        elif choice == "4":
            test_suite.addTest(unittest.makeSuite(TestSearchNode))
            test_suite.addTest(unittest.makeSuite(TestUtilityFunction))
            test_suite.addTest(unittest.makeSuite(TestBestMoveFunction))
            print("\nRunning all function tests...")
        else:
            print("Invalid choice. Running all tests...")
            return run_all_tests()
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(test_suite)
        
        print(f"\nResults: {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")
        return result.wasSuccessful()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        return False
    except Exception as e:
        print(f"\nError running tests: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            success = run_quick_tests()
        elif sys.argv[1] == "interactive":
            success = run_function_specific_tests()
        else:
            print("Usage: python test_all_ai_functions.py [quick|interactive]")
            print("  quick: Run a quick subset of tests")
            print("  interactive: Choose specific functions to test")
            print("  (no args): Run all comprehensive tests")
            success = run_all_tests()
    else:
        success = run_all_tests()
    
    if success:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    
    sys.exit(0 if success else 1)
