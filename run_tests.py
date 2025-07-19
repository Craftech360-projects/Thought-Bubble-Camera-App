"""Run all tests for the Thought Bubble Camera App."""

import sys
import unittest
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Import test modules
from tests.test_bubble import TestBubble
from tests.test_thought_generator import TestThoughtGenerator
from tests.test_person_tracker import TestPersonTracker


def run_all_tests():
    """Run all unit tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestBubble))
    test_suite.addTest(unittest.makeSuite(TestThoughtGenerator))
    test_suite.addTest(unittest.makeSuite(TestPersonTracker))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return success/failure
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running Thought Bubble Camera App Tests")
    print("-" * 50)
    
    success = run_all_tests()
    
    print("-" * 50)
    if success:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed!")
        sys.exit(1)