#!/usr/bin/env python
"""
Simple test script to verify the context pruning implementation.
Run this before running the full crew to check if everything is set up correctly.
"""

import os
import sys

def test_environment():
    """Test environment variables and API keys."""
    print("🔍 Testing Environment Setup...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major == 3 and 10 <= python_version.minor < 14:
        print(f"✅ Python version: {python_version.major}.{python_version.minor}")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor} not supported (need 3.10-3.13)")
        return False
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and len(api_key) > 10:
        print(f"✅ GEMINI_API_KEY found (length: {len(api_key)})")
    else:
        print("❌ GEMINI_API_KEY not found or invalid in .env file")
        return False
    
    return True

def test_imports():
    """Test if all required packages are installed."""
    print("\n📦 Testing Package Imports...")
    
    required_packages = [
        ("crewai", "CrewAI"),
        ("langchain", "LangChain"),
        ("langchain_google_genai", "LangChain Google GenAI"),
        ("langchain_community", "LangChain Community"),
        ("langchain_core", "LangChain Core"),
        ("langchain_text_splitters", "LangChain Text Splitters"),
    ]
    
    all_imported = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name} imported successfully")
        except ImportError as e:
            print(f"❌ {name} import failed: {e}")
            all_imported = False
    
    return all_imported

def test_tools():
    """Test if custom tools can be imported."""
    print("\n🛠️  Testing Custom Tools...")
    
    try:
        from context_pruning.tools.custom_tool import RAGRetrievalTool, ContextPruningTool
        print("✅ RAGRetrievalTool imported")
        print("✅ ContextPruningTool imported")
        
        # Try to instantiate (but don't run)
        rag_tool = RAGRetrievalTool()
        pruning_tool = ContextPruningTool()
        print("✅ Tools instantiated successfully")
        
        return True
    except Exception as e:
        print(f"❌ Tool import/instantiation failed: {e}")
        return False

def test_crew():
    """Test if crew can be imported and instantiated."""
    print("\n👥 Testing Crew Setup...")
    
    try:
        from context_pruning.crew import ContextPruning
        print("✅ ContextPruning crew imported")
        
        crew_instance = ContextPruning()
        print("✅ Crew instantiated successfully")
        
        # Check agents
        print(f"✅ Found {len(crew_instance.agents)} agents")
        
        # Check tasks
        print(f"✅ Found {len(crew_instance.tasks)} tasks")
        
        return True
    except Exception as e:
        print(f"❌ Crew setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Context Pruning - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Environment", test_environment),
        ("Package Imports", test_imports),
        ("Custom Tools", test_tools),
        ("Crew Setup", test_crew),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to run the crew.")
        print("\nNext steps:")
        print("  1. Run: crewai run")
        print("  2. Check output: cat context_pruning_result.md")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Run: crewai install")
        print("  - Check .env file has GEMINI_API_KEY")
        print("  - Ensure Python version is 3.10-3.13")
        return 1

if __name__ == "__main__":
    sys.exit(main())
