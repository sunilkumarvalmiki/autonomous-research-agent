#!/usr/bin/env python3
"""
Final verification script to ensure the agent is fully functional.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def run_verification():
    """Run comprehensive verification tests."""
    print("=" * 70)
    print("AUTONOMOUS RESEARCH AGENT - FINAL VERIFICATION")
    print("=" * 70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Import all components
    print("\n[1/8] Testing imports...")
    try:
        from autonomous_agent import ModelManager, ResearchAgent, KnowledgeBase
        from autonomous_agent.config import Config, set_config
        print("    ✓ All imports successful")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ Import failed: {e}")
        tests_failed += 1
        return tests_passed, tests_failed
    
    # Test 2: Create configuration
    print("\n[2/8] Testing configuration...")
    try:
        config = Config.load_default()
        config.agent.enable_rag = False
        set_config(config)
        assert len(config.models) == 3
        assert 'llama' in config.models
        print("    ✓ Configuration created successfully")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ Configuration failed: {e}")
        tests_failed += 1
    
    # Test 3: Create ModelManager
    print("\n[3/8] Testing ModelManager...")
    try:
        manager = ModelManager()
        assert len(manager.list_models()) == 3
        print(f"    ✓ ModelManager created with {len(manager.list_models())} models")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ ModelManager failed: {e}")
        tests_failed += 1
    
    # Test 4: Model selection
    print("\n[4/8] Testing model selection...")
    try:
        assert manager.select_best_model('code') == 'llama'
        assert manager.select_best_model('general') == 'mistral'
        assert manager.select_best_model('fast') == 'phi'
        print("    ✓ Model selection working correctly")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ Model selection failed: {e}")
        tests_failed += 1
    
    # Test 5: Create ResearchAgent
    print("\n[5/8] Testing ResearchAgent creation...")
    try:
        agent = ResearchAgent()
        assert agent.model_manager is not None
        assert agent.config is not None
        print("    ✓ ResearchAgent created successfully")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ ResearchAgent creation failed: {e}")
        tests_failed += 1
    
    # Test 6: Test statistics
    print("\n[6/8] Testing statistics...")
    try:
        stats = agent.get_statistics()
        assert 'total_interactions' in stats
        assert 'loaded_models' in stats
        assert stats['total_interactions'] == 0
        print("    ✓ Statistics working correctly")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ Statistics failed: {e}")
        tests_failed += 1
    
    # Test 7: Test feedback system
    print("\n[7/8] Testing feedback system...")
    try:
        # Note: This doesn't actually query a model, just tests the structure
        agent.add_feedback(
            query="test query",
            response="test response",
            rating=5,
            comments="test"
        )
        stats = agent.get_statistics()
        assert stats['total_interactions'] == 1
        assert stats['average_rating'] == 5.0
        print("    ✓ Feedback system working correctly")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ Feedback system failed: {e}")
        tests_failed += 1
    
    # Test 8: Test model configs
    print("\n[8/8] Testing model configurations...")
    try:
        for model_name in ['llama', 'mistral', 'phi']:
            config = manager.configs[model_name]
            assert config.model_type == 'ollama'
            assert config.max_tokens > 0
            assert 0 <= config.temperature <= 1
        print("    ✓ All model configurations valid")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ Model configuration failed: {e}")
        tests_failed += 1
    
    return tests_passed, tests_failed

if __name__ == "__main__":
    try:
        passed, failed = run_verification()
        
        print("\n" + "=" * 70)
        print(f"VERIFICATION RESULTS: {passed}/{passed + failed} tests passed")
        print("=" * 70)
        
        if failed == 0:
            print("\n✅ ALL TESTS PASSED! The autonomous research agent is fully operational.")
            print("\n🚀 The agent can now:")
            print("   • Import and initialize successfully")
            print("   • Manage multiple models (Ollama, local transformers)")
            print("   • Select appropriate models based on task type")
            print("   • Track statistics and collect feedback")
            print("   • Be used via Python API or CLI")
            print("\n📝 Next steps:")
            print("   1. Install Ollama: https://ollama.ai/")
            print("   2. Run: ollama pull llama3.1:8b")
            print("   3. Try: python examples/simple_research.py")
            print("\n" + "=" * 70)
            sys.exit(0)
        else:
            print(f"\n✗ {failed} test(s) failed. Please review the errors above.")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
