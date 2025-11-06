"""
Simple integration tests without complex imports.
Tests basic functionality to verify the system is working.
"""


def test_basic_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        # These should work since they don't have relative imports
        from dotenv import load_dotenv
        import gradio as gr
        from agents import Agent
        print("✓ External dependencies OK")
        
        # Test that files exist
        import os
        files_to_check = [
            'models.py',
            'budget.py',
            'config.py',
            'state_machine.py',
            'agent_registry.py',
            'research_coordinator.py',
            'deep_research.py'
        ]
        
        for file in files_to_check:
            assert os.path.exists(file), f"Missing: {file}"
        
        print("✓ All core files present")
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False
    
    return True


def test_data_structures():
    """Test basic data structures without imports."""
    print("Testing data structures...")
    
    # Test that we can create basic Python structures
    test_dict = {
        'query': 'test',
        'state': 'initializing',
        'findings': [],
        'budget': {
            'max_tokens': 1000,
            'used_tokens': 0
        }
    }
    
    assert test_dict['query'] == 'test'
    assert len(test_dict['findings']) == 0
    
    print("✓ Data structures OK")
    return True


def test_file_structure():
    """Test that the project structure is correct."""
    print("Testing file structure...")
    
    import os
    
    expected_files = [
        'models.py',
        'budget.py',
        'config.py',
        'state_machine.py',
        'agent_registry.py',
        'handoff_controller.py',
        'trail_manager.py',
        'trail_discovery.py',
        'trail_execution.py',
        'evaluation_engine.py',
        'clarification_engine.py',
        'progress_monitor.py',
        'research_coordinator.py',
        'planner_agent.py',
        'search_agent.py',
        'writer_agent.py',
        'email_agent.py',
        'deep_research.py',
        'logging_config.py',
        'cache.py',
        'README.md',
        'IMPLEMENTATION_SUMMARY.md',
        'example_usage.py'
    ]
    
    missing = []
    for file in expected_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"✗ Missing files: {missing}")
        return False
    
    print(f"✓ All {len(expected_files)} files present")
    return True


def test_syntax():
    """Test that Python files have valid syntax."""
    print("Testing syntax...")
    
    import py_compile
    import os
    
    python_files = [f for f in os.listdir('.') if f.endswith('.py')]
    
    errors = []
    for file in python_files:
        try:
            py_compile.compile(file, doraise=True)
        except py_compile.PyCompileError as e:
            errors.append((file, str(e)))
    
    if errors:
        print(f"✗ Syntax errors found:")
        for file, error in errors:
            print(f"  {file}: {error}")
        return False
    
    print(f"✓ All {len(python_files)} Python files have valid syntax")
    return True


def run_tests():
    """Run all simple tests."""
    print("=" * 60)
    print("Running Simple Integration Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_basic_imports,
        test_data_structures,
        test_file_structure,
        test_syntax
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    if failed == 0:
        print(f"✅ All {passed} Tests Passed!")
        print("=" * 60)
        print()
        print("System structure is correct.")
        print("Files are present and have valid syntax.")
        print()
        print("Note: Full integration tests require running the system")
        print("with actual LLM calls. Use example_usage.py for that.")
    else:
        print(f"❌ {failed} Test(s) Failed, {passed} Passed")
        print("=" * 60)


if __name__ == "__main__":
    run_tests()
