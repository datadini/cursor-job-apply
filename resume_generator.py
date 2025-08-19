#!/usr/bin/env python3
"""
Resume Generator Utility
Generates customized resumes for specific job applications
"""

import json
import re
from typing import Dict, List, Optional
import openai
from pathlib import Path

class ResumeGenerator:
    def __init__(self, openai_api_key: str):
        """Initialize the resume generator"""
        openai.api_key = openai_api_key
        
    def load_profile(self, profile_path: str = "profile.md") -> Dict:
        """Load user profile from markdown file"""
        try:
            with open(profile_path, 'r') as file:
                content = file.read()
                return self.parse_profile_markdown(content)
        except FileNotFoundError:
            raise FileNotFoundError(f"Profile file {profile_path} not found. Please create it first.")
    
    def parse_profile_markdown(self, content: str) -> Dict:
        """Parse markdown profile into structured data"""
        profile = {}
        
        # Extract personal information
        name_match = re.search(r'\*\*Name\*\*: \[(.*?)\]', content)
        if name_match:
            profile['name'] = name_match.group(1)
        
        location_match = re.search(r'\*\*Location\*\*: \[(.*?)\]', content)
        if location_match:
            profile['location'] = location_match.group(1)
        
        current_role_match = re.search(r'\*\*Current Role\*\*: \[(.*?)\]', content)
        if current_role_match:
            profile['current_role'] = current_role_match.group(1)
        
        years_exp_match = re.search(r'\*\*Years of Experience\*\*: \[(.*?)\]', content)
        if years_exp_match:
            profile['years_experience'] = years_exp_match.group(1)
        
        # Extract skills by category
        skills = {}
        for category in ['Data Engineering', 'Data Analysis', 'AI Engineering', 'Business Intelligence', 'AI Prototyping']:
            category_content = re.search(f'### {category}(.*?)(?=###|$)', content, re.DOTALL)
            if category_content:
                skills[category] = self.extract_skills_from_text(category_content.group(1))
        
        profile['skills'] = skills
        
        # Extract experience
        experience_matches = re.findall(r'### \[(.*?)\] - \[(.*?)\] \((.*?)\)(.*?)(?=###|$)', content, re.DOTALL)
        profile['experience'] = []
        for match in experience_matches:
            company, position, period, details = match
            profile['experience'].append({
                'company': company,
                'position': position,
                'period': period,
                'details': details.strip()
            })
        
        # Extract education
        education_match = re.search(r'## Education(.*?)(?=##|$)', content, re.DOTALL)
        if education_match:
            profile['education'] = self.extract_education(education_match.group(1))
        
        # Extract certifications
        cert_match = re.search(r'## Certifications(.*?)(?=##|$)', content, re.DOTALL)
        if cert_match:
            profile['certifications'] = self.extract_certifications(cert_match.group(1))
        
        # Extract projects
        projects_match = re.search(r'## Projects & Portfolio(.*?)(?=##|$)', content, re.DOTALL)
        if projects_match:
            profile['projects'] = self.extract_projects(projects_match.group(1))
        
        return profile
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text content"""
        skills = []
        lines = text.split('\n')
        for line in lines:
            if '**' in line and ':' in line:
                skill_text = line.split(':')[1].strip()
                if skill_text and skill_text != '[e.g., ...]' and not skill_text.startswith('['):
                    skills.append(skill_text)
        return skills
    
    def extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        lines = text.split('\n')
        current_edu = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('- **Degree**:'):
                if current_edu:
                    education.append(current_edu)
                current_edu = {'degree': line.split(':', 1)[1].strip()}
            elif line.startswith('- **Institution**:'):
                current_edu['institution'] = line.split(':', 1)[1].strip()
            elif line.startswith('- **Year**:'):
                current_edu['year'] = line.split(':', 1)[1].strip()
            elif line.startswith('- **Relevant Courses**:'):
                current_edu['courses'] = line.split(':', 1)[1].strip()
        
        if current_edu:
            education.append(current_edu)
        
        return education
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certs = []
        lines = text.split('\n')
        for line in lines:
            if line.startswith('- ') and ' - ' in line:
                cert_text = line[2:].strip()
                if cert_text and not cert_text.startswith('['):
                    certs.append(cert_text)
        return certs
    
    def extract_projects(self, text: str) -> List[Dict]:
        """Extract project information"""
        projects = []
        project_blocks = text.split('### ')[1:]  # Skip first empty element
        
        for block in project_blocks:
            lines = block.split('\n')
            project = {}
            
            # First line is project name
            if lines:
                project['name'] = lines[0].strip()
            
            for line in lines[1:]:
                line = line.strip()
                if line.startswith('- **Description**:'):
                    project['description'] = line.split(':', 1)[1].strip()
                elif line.startswith('- **Technologies**:'):
                    project['technologies'] = line.split(':', 1)[1].strip()
                elif line.startswith('- **GitHub**:'):
                    project['github'] = line.split(':', 1)[1].strip()
                elif line.startswith('- **Live Demo**:'):
                    project['demo'] = line.split(':', 1)[1].strip()
            
            if project:
                projects.append(project)
        
        return projects
    
    def generate_customized_resume(self, profile: Dict, job_info: Dict) -> str:
        """Generate a customized resume for a specific job"""
        try:
            # Determine job category and required skills
            job_category = self.categorize_job(job_info['title'])
            job_title = job_info['title']
            company = job_info['company']
            
            # Get relevant skills for this job category
            relevant_skills = self.get_relevant_skills(profile, job_category)
            
            # Create prompt for resume customization
            prompt = f"""
            Create a customized, professional resume for a {job_title} position at {company}.
            
            Job Requirements (inferred from title): {self.get_job_requirements(job_category)}
            
            Candidate Profile:
            - Name: {profile.get('name', '[Your Name]')}
            - Current Role: {profile.get('current_role', '[Current Position]')}
            - Years of Experience: {profile.get('years_experience', '[X]')}
            - Location: {profile.get('location', '[Your Location]')}
            - Relevant Skills: {', '.join(relevant_skills)}
            
            Experience Summary:
            {self.format_experience_for_resume(profile)}
            
            Education: {self.format_education_for_resume(profile)}
            Certifications: {', '.join(profile.get('certifications', []))}
            Projects: {self.format_projects_for_resume(profile)}
            
            Requirements:
            1. Focus on skills and experience most relevant to this specific role
            2. Use action verbs and quantify achievements where possible
            3. Keep it honest - don't exaggerate skills the candidate doesn't have
            4. Format as a clean, professional resume with clear sections
            5. Highlight transferable skills that could be adapted to this role
            6. Keep it to 1-2 pages maximum
            7. Use bullet points for experience and achievements
            8. Include a professional summary at the top
            
            Generate a professional resume that makes the candidate appear as the perfect fit for this specific role.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert resume writer who creates customized, honest, and compelling resumes. Format the output as a clean, professional resume with proper sections and bullet points."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Failed to generate customized resume: {e}")
            return self.get_fallback_resume(profile, job_info)
    
    def categorize_job(self, job_title: str) -> str:
        """Categorize job based on title"""
        title_lower = job_title.lower()
        
        if any(word in title_lower for word in ['data engineer', 'etl', 'pipeline', 'data infrastructure']):
            return 'data_engineer'
        elif any(word in title_lower for word in ['data analyst', 'analytics', 'business analyst']):
            return 'data_analyst'
        elif any(word in title_lower for word in ['ai engineer', 'machine learning', 'ml engineer', 'deep learning']):
            return 'ai_engineer'
        elif any(word in title_lower for word in ['business intelligence', 'bi developer', 'bi engineer', 'dashboard']):
            return 'bi_developer'
        elif any(word in title_lower for word in ['ai prototyper', 'prototype', 'poc', 'rapid prototyping']):
            return 'ai_prototyper'
        else:
            return 'general'
    
    def get_relevant_skills(self, profile: Dict, job_category: str) -> List[str]:
        """Get relevant skills for a specific job category"""
        skill_mapping = {
            'data_engineer': ['Data Engineering', 'Databases', 'Big Data', 'ETL/ELT', 'Cloud Platforms'],
            'data_analyst': ['Data Analysis', 'Programming', 'Analytics Tools', 'Statistical Analysis'],
            'ai_engineer': ['AI Engineering', 'Machine Learning', 'Deep Learning', 'NLP'],
            'bi_developer': ['Business Intelligence', 'BI Tools', 'SQL', 'Data Modeling'],
            'ai_prototyper': ['AI Prototyping', 'Rapid Prototyping', 'User Experience']
        }
        
        relevant_categories = skill_mapping.get(job_category, [])
        skills = []
        
        for category in relevant_categories:
            if category in profile.get('skills', {}):
                skills.extend(profile['skills'][category])
        
        return skills[:12]  # Limit to top 12 skills
    
    def get_job_requirements(self, job_category: str) -> str:
        """Get typical job requirements for a category"""
        requirements = {
            'data_engineer': 'Data pipeline development, ETL/ELT processes, database management, cloud platforms, big data technologies, data infrastructure',
            'data_analyst': 'Data analysis, statistical analysis, data visualization, SQL, analytics tools, business insights, reporting',
            'ai_engineer': 'Machine learning, deep learning, model development, MLOps, AI/ML frameworks, algorithm optimization',
            'bi_developer': 'Business intelligence tools, dashboard development, data modeling, SQL, KPI tracking, data visualization',
            'ai_prototyper': 'Rapid prototyping, proof of concepts, user experience design, AI/ML integration, iterative development'
        }
        
        return requirements.get(job_category, 'General technical skills and problem-solving abilities')
    
    def format_experience_for_resume(self, profile: Dict) -> str:
        """Format experience for resume generation"""
        experience_text = ""
        for exp in profile.get('experience', []):
            experience_text += f"{exp['position']} at {exp['company']} ({exp['period']}): {exp['details']}\n"
        return experience_text
    
    def format_education_for_resume(self, profile: Dict) -> str:
        """Format education for resume generation"""
        education_text = ""
        for edu in profile.get('education', []):
            education_text += f"{edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('year', '')})\n"
        return education_text
    
    def format_projects_for_resume(self, profile: Dict) -> str:
        """Format projects for resume generation"""
        projects_text = ""
        for proj in profile.get('projects', []):
            projects_text += f"{proj.get('name', '')}: {proj.get('description', '')} - {proj.get('technologies', '')}\n"
        return projects_text
    
    def get_fallback_resume(self, profile: Dict, job_info: Dict) -> str:
        """Get a fallback resume if AI generation fails"""
        return f"""
{profile.get('name', '[Your Name]')}
{profile.get('location', '[Your Location]')} | [Your Email] | [Your Phone]

PROFESSIONAL SUMMARY
Experienced {profile.get('current_role', 'data professional')} with expertise in data engineering, analysis, and AI development. 
Passionate about leveraging technology to solve complex business problems and drive data-driven decision making.

SKILLS
{', '.join(self.get_relevant_skills(profile, 'general'))}

EXPERIENCE
{self.format_experience_for_resume(profile)}

EDUCATION
{self.format_education_for_resume(profile)}

CERTIFICATIONS
{', '.join(profile.get('certifications', []))}

PROJECTS
{self.format_projects_for_resume(profile)}
        """
    
    def save_resume(self, resume_content: str, filename: str):
        """Save resume to file"""
        try:
            with open(filename, 'w') as file:
                file.write(resume_content)
            print(f"Resume saved to {filename}")
        except Exception as e:
            print(f"Failed to save resume: {e}")
    
    def generate_resume_for_job(self, job_title: str, company: str, output_file: str = None):
        """Generate a resume for a specific job"""
        try:
            # Load profile
            profile = self.load_profile()
            
            # Create job info
            job_info = {
                'title': job_title,
                'company': company
            }
            
            # Generate customized resume
            resume = self.generate_customized_resume(profile, job_info)
            
            # Save resume
            if output_file:
                self.save_resume(resume, output_file)
            else:
                output_file = f"resume_{company.lower().replace(' ', '_')}_{job_title.lower().replace(' ', '_')}.txt"
                self.save_resume(resume, output_file)
            
            return resume
            
        except Exception as e:
            print(f"Failed to generate resume: {e}")
            return None

def main():
    """Main function for command line usage"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python resume_generator.py <job_title> <company> [output_file]")
        print("Example: python resume_generator.py 'Data Engineer' 'Google'")
        return
    
    job_title = sys.argv[1]
    company = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Check if OpenAI API key is set
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your_key_here'")
        return
    
    try:
        generator = ResumeGenerator(os.getenv('OPENAI_API_KEY'))
        generator.generate_resume_for_job(job_title, company, output_file)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()