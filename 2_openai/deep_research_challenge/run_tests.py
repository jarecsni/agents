#!/usr/bin/env python
"""
Test runner for all unit and integration tests.
"""
import sys
import subprocess


def run_tests():
    """Run all tests using pytest."""
    print("=" * 60)
    print("Running All Tests")
    print("=" * 60)
    print()
    
    # Run pytest on tests directory
    result = subprocess.run(
        ["pytest", "tests/", "-v", "--tb=short"],
        capture_output=False
    )
    
    return result.returncode


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
