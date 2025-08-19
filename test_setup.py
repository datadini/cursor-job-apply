#!/usr/bin/env python3
"""
Test Setup Script
Verifies that all components of the LinkedIn automation system are working
"""

import os
import sys
import importlib
import yaml
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'selenium',
        'undetected_chromedriver',
        'openai',
        'yaml',
        'requests',
        'beautifulsoup4'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing packages: pip install -r requirements.txt")
        return False
    else:
        print("✅ All packages imported successfully")
        return True

def test_config_file():
    """Test if configuration file exists and is valid"""
    print("\n🔍 Testing configuration file...")
    
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ config.yaml not found")
        return False
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Check required fields
        required_fields = ['linkedin', 'openai_api_key', 'job_search']
        missing_fields = []
        
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields: {', '.join(missing_fields)}")
            return False
        
        print("✅ config.yaml is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading config.yaml: {e}")
        return False

def test_profile_file():
    """Test if profile file exists and has required sections"""
    print("\n🔍 Testing profile file...")
    
    profile_path = Path("profile.md")
    if not profile_path.exists():
        print("❌ profile.md not found")
        return False
    
    try:
        with open(profile_path, 'r') as file:
            content = file.read()
        
        # Check for required sections
        required_sections = [
            '## Personal Information',
            '## Core Skills & Technologies',
            '## Professional Experience',
            '## Personal Notes for Cover Letters'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing required sections: {', '.join(missing_sections)}")
            return False
        
        # Check for placeholder values
        placeholder_patterns = [
            r'\[Your Name\]',
            r'\[Your Current Position\]',
            r'\[X\] years',
            r'\[e\.g\., \.\.\.\]'
        ]
        
        placeholder_count = 0
        for pattern in placeholder_patterns:
            if re.search(pattern, content):
                placeholder_count += 1
        
        if placeholder_count > 0:
            print(f"⚠️  Found {placeholder_count} placeholder values - please fill these in")
            return False
        
        print("✅ profile.md is properly configured")
        return True
        
    except Exception as e:
        print(f"❌ Error reading profile.md: {e}")
        return False

def test_openai_api():
    """Test OpenAI API connection"""
    print("\n🔍 Testing OpenAI API...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set: export OPENAI_API_KEY='your_key_here'")
        return False
    
    if api_key == 'your_openai_api_key_here':
        print("❌ OPENAI_API_KEY is still set to placeholder value")
        return False
    
    try:
        import openai
        openai.api_key = api_key
        
        # Test with a simple API call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ OpenAI API connection successful")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def test_resume_generator():
    """Test resume generator functionality"""
    print("\n🔍 Testing resume generator...")
    
    try:
        from resume_generator import ResumeGenerator
        
        # Test profile parsing
        generator = ResumeGenerator("test_key")
        profile = generator.load_profile()
        
        if not profile:
            print("❌ Failed to load profile")
            return False
        
        print("✅ Resume generator is working")
        return True
        
    except Exception as e:
        print(f"❌ Resume generator test failed: {e}")
        return False

def test_linkedin_agent():
    """Test LinkedIn agent initialization"""
    print("\n🔍 Testing LinkedIn agent...")
    
    try:
        from linkedin_job_agent import LinkedInJobAgent
        
        # Test agent initialization (without running)
        agent = LinkedInJobAgent()
        
        if not agent.config:
            print("❌ Failed to load configuration")
            return False
        
        print("✅ LinkedIn agent initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ LinkedIn agent test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 LinkedIn Job Automation System - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_file,
        test_profile_file,
        test_openai_api,
        test_resume_generator,
        test_linkedin_agent
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready to use.")
        print("\nNext steps:")
        print("1. Fill in your profile.md with actual information")
        print("2. Update config.yaml with your credentials")
        print("3. Set your OpenAI API key")
        print("4. Run: python linkedin_job_agent.py")
    else:
        print("❌ Some tests failed. Please fix the issues above before proceeding.")
        print("\nCommon fixes:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Fill in profile.md with your information")
        print("- Update config.yaml with your credentials")
        print("- Set OPENAI_API_KEY environment variable")
    
    return passed == total

if __name__ == "__main__":
    import re
    success = main()
    sys.exit(0 if success else 1)