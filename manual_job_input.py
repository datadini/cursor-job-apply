#!/usr/bin/env python3
"""
Manual Job Input Utility
Allows you to manually input job descriptions and requirements for testing resume generation
"""

import os
import sys
from resume_generator import ResumeGenerator

def get_job_input():
    """Get job information from user input"""
    print("📝 Manual Job Input for Resume Generation")
    print("=" * 50)
    
    # Get basic job info
    job_title = input("Enter job title: ").strip()
    if not job_title:
        print("❌ Job title is required")
        return None
    
    company = input("Enter company name: ").strip()
    if not company:
        print("❌ Company name is required")
        return None
    
    # Get job description
    print("\n📋 Enter the job description (press Enter twice when done):")
    print("(You can copy-paste from LinkedIn or any job posting)")
    
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    
    job_description = "\n".join(lines[:-1])  # Remove the last empty line
    
    if not job_description.strip():
        print("⚠️  No job description provided, will use generic requirements")
        job_description = None
    
    # Get specific requirements
    print("\n🎯 Enter specific job requirements (one per line, press Enter twice when done):")
    print("Examples: '5+ years Python experience', 'Knowledge of AWS', 'SQL proficiency'")
    
    requirements = []
    while True:
        req = input()
        if req == "" and requirements and requirements[-1] == "":
            break
        requirements.append(req)
    
    job_requirements = [r.strip() for r in requirements[:-1] if r.strip()]  # Remove empty lines
    
    if not job_requirements:
        print("⚠️  No specific requirements provided")
        job_requirements = None
    
    return {
        'title': job_title,
        'company': company,
        'description': job_description,
        'requirements': job_requirements
    }

def main():
    """Main function"""
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your_key_here'")
        return
    
    try:
        # Get job input
        job_data = get_job_input()
        if not job_data:
            return
        
        print(f"\n✅ Job information collected:")
        print(f"Title: {job_data['title']}")
        print(f"Company: {job_data['company']}")
        print(f"Description length: {len(job_data['description']) if job_data['description'] else 0} characters")
        print(f"Requirements: {len(job_data['requirements']) if job_data['requirements'] else 0} items")
        
        # Confirm before proceeding
        confirm = input("\n🤔 Proceed with resume generation? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Resume generation cancelled")
            return
        
        # Initialize resume generator
        generator = ResumeGenerator(os.getenv('OPENAI_API_KEY'))
        
        print("\n🚀 Generating customized resume...")
        
        # Generate resume
        resume = generator.generate_customized_resume(
            profile=generator.load_profile(),
            job_info={'title': job_data['title'], 'company': job_data['company']},
            job_description=job_data['description'],
            job_requirements=job_data['requirements']
        )
        
        if resume:
            # Save resume
            filename = f"resume_{job_data['company'].lower().replace(' ', '_')}_{job_data['title'].lower().replace(' ', '_')}.txt"
            generator.save_resume(resume, filename)
            
            print(f"\n🎉 Resume generated successfully!")
            print(f"📁 Saved to: {filename}")
            
            # Show preview
            print("\n📄 Resume Preview (first 500 characters):")
            print("-" * 50)
            print(resume[:500] + "..." if len(resume) > 500 else resume)
            print("-" * 50)
            
        else:
            print("❌ Failed to generate resume")
            
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()