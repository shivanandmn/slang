#!/usr/bin/env python3
"""
CI testing script for Slang LiveKit Agent
This script validates the build environment in CI/CD pipelines.
"""

import sys

def check_dependencies():
    """Check if all required packages are installed."""
    try:
        import livekit
        print("✅ LiveKit agents package installed")
        
        import openai
        print("✅ OpenAI package available")
        
        from livekit.plugins import deepgram, elevenlabs, silero
        print("✅ All LiveKit plugins available")
        
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def check_python_syntax():
    """Check if the main agent file has valid Python syntax."""
    try:
        import ast
        with open('multi_agent.py', 'r') as f:
            source = f.read()
        ast.parse(source)
        print("✅ Python syntax validation passed")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in multi_agent.py: {e}")
        return False
    except FileNotFoundError:
        print("❌ multi_agent.py not found")
        return False

def check_dockerfile():
    """Check if Dockerfile exists and has basic structure."""
    try:
        with open('Dockerfile', 'r') as f:
            content = f.read()
        
        required_elements = ['FROM', 'WORKDIR', 'COPY', 'RUN', 'CMD']
        missing = [elem for elem in required_elements if elem not in content]
        
        if missing:
            print(f"❌ Dockerfile missing elements: {missing}")
            return False
        
        print("✅ Dockerfile structure validation passed")
        return True
    except FileNotFoundError:
        print("❌ Dockerfile not found")
        return False

def main():
    """Run all CI validation checks."""
    print("🔍 Running CI Build Validation\n")
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Python Syntax", check_python_syntax),
        ("Dockerfile", check_dockerfile)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"Checking {name}...")
        if not check_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All CI validation checks passed!")
        print("   Build environment is ready for deployment")
    else:
        print("❌ CI validation failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
