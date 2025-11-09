#!/usr/bin/env python3
"""
Local testing script for Slang LiveKit Agent
This script helps validate the environment and configuration before running the agent.
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set."""
    load_dotenv()
    
    required_vars = [
        'LIVEKIT_URL',
        'LIVEKIT_API_KEY', 
        'LIVEKIT_API_SECRET',
        'OPENAI_API_KEY',
        'DEEPGRAM_API_KEY',
        'ELEVEN_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease check your .env file and ensure all variables are set.")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_dependencies():
    """Check if all required packages are installed."""
    try:
        import livekit
        import openai
        print("✅ Core dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def validate_api_keys():
    """Basic validation of API key formats."""
    load_dotenv()
    
    livekit_url = os.getenv('LIVEKIT_URL')
    openai_key = os.getenv('OPENAI_API_KEY')
    deepgram_key = os.getenv('DEEPGRAM_API_KEY')
    eleven_key = os.getenv('ELEVEN_API_KEY')
    
    issues = []
    
    if livekit_url and not livekit_url.startswith('wss://'):
        issues.append("LIVEKIT_URL should start with 'wss://'")
    
    if openai_key and not openai_key.startswith('sk-'):
        issues.append("OPENAI_API_KEY should start with 'sk-'")
    
    if eleven_key and not eleven_key.startswith('sk_'):
        issues.append("ELEVEN_API_KEY should start with 'sk_'")
    
    if issues:
        print("⚠️  API key format warnings:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("✅ API key formats look correct")
    return True

def main():
    """Run all validation checks."""
    print("🔍 Running Slang Agent Local Test Validation\n")
    
    checks = [
        ("Environment Variables", check_environment),
        ("Dependencies", check_dependencies), 
        ("API Key Formats", validate_api_keys)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"Checking {name}...")
        if not check_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All checks passed! You can now run:")
        print("   python multi_agent.py")
        print("\nOr test with Docker:")
        print("   docker build -t slang-agent .")
        print("   docker run --env-file .env slang-agent")
    else:
        print("❌ Some checks failed. Please fix the issues above before running the agent.")
        sys.exit(1)

if __name__ == "__main__":
    main()
