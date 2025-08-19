#!/usr/bin/env python3
"""
LinkedIn Job Application Automation Agent
Automatically applies to data engineering, AI, and BI roles in Singapore/Hong Kong
"""

import json
import time
import random
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yaml
from pathlib import Path
import openai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInJobAgent:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the LinkedIn Job Agent"""
        self.config = self.load_config(config_path)
        self.profile = self.load_profile()
        self.driver = None
        self.jobs_applied = []
        self.session_start = datetime.now()
        
        # OpenAI configuration
        openai.api_key = self.config.get('openai_api_key')
        
        # Human-like behavior settings
        self.min_delay = 3
        self.max_delay = 8
        self.break_interval = 15  # Take a break every 15 applications
        self.break_duration = (30, 120)  # Random break between 30-120 seconds
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"Config file {config_path} not found. Creating default config.")
            return self.create_default_config()
    
    def create_default_config(self) -> Dict:
        """Create default configuration"""
        config = {
            'linkedin': {
                'email': 'your_email@example.com',
                'password': 'your_password',
                'headless': False,
                'slow_mode': True
            },
            'openai_api_key': 'your_openai_api_key_here',
            'job_search': {
                'keywords': ['data engineer', 'data analyst', 'ai engineer', 'business intelligence developer', 'ai prototyper'],
                'locations': ['Singapore', 'Hong Kong'],
                'experience_levels': ['Entry level', 'Associate', 'Mid-Senior level'],
                'max_applications_per_session': 50,
                'min_delay_between_applications': 3,
                'max_delay_between_applications': 8
            },
            'resume_customization': {
                'max_skills_to_highlight': 8,
                'achievement_focus': True,
                'quantify_results': True
            }
        }
        
        with open('config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        
        return config
    
    def load_profile(self) -> Dict:
        """Load user profile from markdown file"""
        try:
            with open('profile.md', 'r') as file:
                content = file.read()
                return self.parse_profile_markdown(content)
        except FileNotFoundError:
            logger.error("profile.md not found. Please create it first.")
            return {}
    
    def parse_profile_markdown(self, content: str) -> Dict:
        """Parse markdown profile into structured data"""
        profile = {}
        
        # Extract personal information
        name_match = re.search(r'\*\*Name\*\*: \[(.*?)\]', content)
        if name_match:
            profile['name'] = name_match.group(1)
        
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
        
        # Extract personal notes
        notes_match = re.search(r'### Personal Notes for Cover Letters(.*?)(?=##|$)', content, re.DOTALL)
        if notes_match:
            profile['personal_notes'] = notes_match.group(1).strip()
        
        return profile
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text content"""
        skills = []
        lines = text.split('\n')
        for line in lines:
            if '**' in line and ':' in line:
                skill_text = line.split(':')[1].strip()
                if skill_text and skill_text != '[e.g., ...]':
                    skills.append(skill_text)
        return skills
    
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        try:
            options = Options()
            
            if self.config['linkedin']['headless']:
                options.add_argument('--headless')
            
            # Anti-detection measures
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Random user agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # Use undetected-chromedriver for better anti-detection
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome driver setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def login_to_linkedin(self):
        """Login to LinkedIn with anti-detection measures"""
        try:
            logger.info("Attempting to login to LinkedIn...")
            
            self.driver.get("https://www.linkedin.com/login")
            self.human_delay(2, 4)
            
            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            self.human_type(email_field, self.config['linkedin']['email'])
            self.human_delay(1, 2)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            self.human_type(password_field, self.config['linkedin']['password'])
            self.human_delay(1, 2)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".global-nav"))
            )
            
            logger.info("Successfully logged in to LinkedIn")
            self.human_delay(3, 6)
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise
    
    def extract_job_info(self, job_card) -> Optional[Dict]:
        """Extract job information from job card"""
        try:
            # Extract basic job info
            title = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__title").text.strip()
            company = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__subtitle").text.strip()
            location = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__location").text.strip()
            
            # Extract job ID from the card
            job_link = job_card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            job_id = job_link.split("/")[-2] if "/" in job_link else None
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'job_id': job_id,
                'job_url': job_link,
                'keyword_matched': self.get_matching_keyword(title)
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract job info: {e}")
            return None
    
    def get_job_description(self, job_info: Dict) -> Dict:
        """Extract detailed job description and requirements from job page"""
        try:
            logger.info(f"Extracting job description for {job_info['title']} at {job_info['company']}")
            
            # Navigate to job page
            self.driver.get(job_info['job_url'])
            self.human_delay(3, 6)
            
            # Wait for job description to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job-description"))
                )
            except TimeoutException:
                logger.warning("Job description not found, trying alternative selectors")
            
            # Extract job description
            description = ""
            try:
                # Try multiple selectors for job description
                selectors = [
                    ".job-description",
                    ".description__text",
                    ".show-more-less-html__markup",
                    "[data-job-description]"
                ]
                
                for selector in selectors:
                    try:
                        desc_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        description = desc_element.text.strip()
                        if description:
                            break
                    except NoSuchElementException:
                        continue
                
                if not description:
                    # Fallback: try to get any text content from the page
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    description = body.text[:5000]  # Limit to first 5000 characters
                    
            except Exception as e:
                logger.warning(f"Failed to extract job description: {e}")
                description = ""
            
            # Extract job requirements/skills
            requirements = self.extract_job_requirements()
            
            # Extract company information
            company_info = self.extract_company_info()
            
            # Extract job details (experience level, job type, etc.)
            job_details = self.extract_job_details()
            
            job_info.update({
                'description': description,
                'requirements': requirements,
                'company_info': company_info,
                'job_details': job_details
            })
            
            logger.info(f"Successfully extracted job description ({len(description)} chars) and {len(requirements)} requirements")
            return job_info
            
        except Exception as e:
            logger.error(f"Failed to extract job description: {e}")
            return job_info
    
    def extract_job_requirements(self) -> List[str]:
        """Extract job requirements and skills from the job description"""
        try:
            requirements = []
            
            # Look for requirements section
            requirement_selectors = [
                ".job-criteria-item__text",
                ".description__job-criteria-text",
                ".job-criteria-item",
                "[data-test-id='job-criteria-item']"
            ]
            
            for selector in requirement_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 3:
                            requirements.append(text)
                    if requirements:
                        break
                except NoSuchElementException:
                    continue
            
            # If no structured requirements found, try to extract from description
            if not requirements:
                try:
                    desc_element = self.driver.find_element(By.CSS_SELECTOR, ".job-description, .description__text")
                    desc_text = desc_element.text.lower()
                    
                    # Look for common requirement patterns
                    requirement_patterns = [
                        r'requirements?:?\s*([^.]*)',
                        r'qualifications?:?\s*([^.]*)',
                        r'skills?:?\s*([^.]*)',
                        r'experience?:?\s*([^.]*)',
                        r'knowledge of\s*([^.]*)',
                        r'proficiency in\s*([^.]*)',
                        r'familiarity with\s*([^.]*)'
                    ]
                    
                    for pattern in requirement_patterns:
                        matches = re.findall(pattern, desc_text)
                        for match in matches:
                            if match.strip() and len(match.strip()) > 5:
                                requirements.append(match.strip())
                    
                    # Remove duplicates and clean up
                    requirements = list(set(requirements))
                    requirements = [req for req in requirements if len(req) > 5 and len(req) < 200]
                    
                except Exception as e:
                    logger.warning(f"Failed to extract requirements from description: {e}")
            
            return requirements[:20]  # Limit to top 20 requirements
            
        except Exception as e:
            logger.warning(f"Failed to extract job requirements: {e}")
            return []
    
    def extract_company_info(self) -> Dict:
        """Extract company information from the job page"""
        try:
            company_info = {}
            
            # Try to extract company size, industry, etc.
            try:
                company_size_element = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='company-size']")
                company_info['size'] = company_size_element.text.strip()
            except NoSuchElementException:
                pass
            
            try:
                industry_element = self.driver.find_element(By.CSS_SELECTOR, "[data-test-id='company-industry']")
                company_info['industry'] = industry_element.text.strip()
            except NoSuchElementException:
                pass
            
            try:
                company_description = self.driver.find_element(By.CSS_SELECTOR, ".company-description, .about-us__description")
                company_info['description'] = company_description.text.strip()[:500]
            except NoSuchElementException:
                pass
            
            return company_info
            
        except Exception as e:
            logger.warning(f"Failed to extract company info: {e}")
            return {}
    
    def extract_job_details(self) -> Dict:
        """Extract job details like experience level, job type, etc."""
        try:
            job_details = {}
            
            # Look for job criteria
            criteria_selectors = [
                ".job-criteria-item",
                ".description__job-criteria-item"
            ]
            
            for selector in criteria_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            label_element = element.find_element(By.CSS_SELECTOR, ".job-criteria-item__label")
                            value_element = element.find_element(By.CSS_SELECTOR, ".job-criteria-item__text")
                            
                            label = label_element.text.strip().lower()
                            value = value_element.text.strip()
                            
                            if label and value:
                                job_details[label] = value
                        except NoSuchElementException:
                            continue
                except NoSuchElementException:
                    continue
            
            return job_details
            
        except Exception as e:
            logger.warning(f"Failed to extract job details: {e}")
            return {}
    
    def search_jobs(self, keyword: str, location: str) -> List[Dict]:
        """Search for jobs with given keyword and location"""
        try:
            logger.info(f"Searching for jobs: {keyword} in {location}")
            
            # Navigate to jobs page
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}&f_E=2%2C3%2C4"
            self.driver.get(search_url)
            self.human_delay(3, 6)
            
            jobs = []
            page = 1
            max_pages = 5  # Limit to avoid detection
            
            while page <= max_pages and len(jobs) < 20:
                # Extract job listings
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
                
                for card in job_cards:
                    try:
                        job_info = self.extract_job_info(card)
                        if job_info and self.is_job_suitable(job_info):
                            # Extract detailed job description
                            detailed_job = self.get_job_description(job_info)
                            jobs.append(detailed_job)
                            
                            # Add delay between job detail extractions
                            self.human_delay(2, 4)
                    except Exception as e:
                        logger.warning(f"Failed to extract job info: {e}")
                        continue
                
                # Check if there's a next page
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
                    if next_button.is_enabled():
                        next_button.click()
                        self.human_delay(4, 7)
                        page += 1
                    else:
                        break
                except NoSuchElementException:
                    break
            
            logger.info(f"Found {len(jobs)} suitable jobs for {keyword} in {location}")
            return jobs
            
        except Exception as e:
            logger.error(f"Job search failed: {e}")
            return []
    
    def get_matching_keyword(self, job_title: str) -> str:
        """Determine which keyword category the job matches"""
        title_lower = job_title.lower()
        
        if any(word in title_lower for word in ['data engineer', 'etl', 'pipeline']):
            return 'data_engineer'
        elif any(word in title_lower for word in ['data analyst', 'analytics']):
            return 'data_analyst'
        elif any(word in title_lower for word in ['ai engineer', 'machine learning', 'ml engineer']):
            return 'ai_engineer'
        elif any(word in title_lower for word in ['business intelligence', 'bi developer', 'bi engineer']):
            return 'bi_developer'
        elif any(word in title_lower for word in ['ai prototyper', 'prototype', 'poc']):
            return 'ai_prototyper'
        else:
            return 'general'
    
    def is_job_suitable(self, job_info: Dict) -> bool:
        """Check if job is suitable based on criteria"""
        # Check if already applied
        if any(job['job_id'] == job_info['job_id'] for job in self.jobs_applied):
            return False
        
        # Check location preference
        location = job_info['location'].lower()
        if 'singapore' not in location and 'hong kong' not in location:
            return False
        
        # Check if it's a relevant role
        if job_info['keyword_matched'] == 'general':
            return False
        
        return True
    
    def generate_customized_resume(self, job_info: Dict) -> str:
        """Generate a customized resume for the specific job"""
        try:
            # Determine job category and required skills
            job_category = job_info['keyword_matched']
            job_title = job_info['title']
            company = job_info['company']
            
            # Get detailed job information
            job_description = job_info.get('description', '')
            job_requirements = job_info.get('requirements', [])
            company_info = job_info.get('company_info', {})
            job_details = job_info.get('job_details', {})
            
            # Get relevant skills for this job category
            relevant_skills = self.get_relevant_skills(job_category)
            
            # Create comprehensive prompt for resume customization
            prompt = f"""
            Create a customized, professional resume for a {job_title} position at {company}.
            
            JOB DETAILS:
            - Title: {job_title}
            - Company: {company}
            - Company Size: {company_info.get('size', 'Not specified')}
            - Industry: {company_info.get('industry', 'Not specified')}
            - Experience Level: {job_details.get('seniority level', 'Not specified')}
            - Employment Type: {job_details.get('employment type', 'Not specified')}
            
            JOB DESCRIPTION:
            {job_description[:2000] if job_description else 'No detailed description available'}
            
            SPECIFIC JOB REQUIREMENTS:
            {chr(10).join([f"- {req}" for req in job_requirements[:15]]) if job_requirements else 'No specific requirements listed'}
            
            CANDIDATE PROFILE:
            - Skills: {', '.join(relevant_skills)}
            - Experience: {self.format_experience_for_resume()}
            
            RESUME CUSTOMIZATION REQUIREMENTS:
            1. Analyze the specific job description and requirements above
            2. Focus on skills and experience that directly match what they're looking for
            3. Use action verbs and quantify achievements where possible
            4. Keep it honest - don't exaggerate skills the candidate doesn't have
            5. Format as a clean, professional resume with clear sections
            6. Highlight transferable skills that could be adapted to this specific role
            7. Keep it to 1-2 pages maximum
            8. Use bullet points for experience and achievements
            9. Include a professional summary that directly addresses this role
            10. Tailor the skills section to match the job requirements
            11. Customize experience descriptions to align with the role's needs
            12. Reference specific technologies/tools mentioned in the job requirements
            
            Generate a professional resume that makes the candidate appear as the perfect fit for this specific role by directly addressing the job requirements and company needs.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert resume writer who creates highly customized, honest, and compelling resumes. You analyze job descriptions in detail and tailor resumes to be the perfect match for specific roles. Format the output as a clean, professional resume with proper sections and bullet points."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate customized resume: {e}")
            return self.get_fallback_resume()
    
    def get_relevant_skills(self, job_category: str) -> List[str]:
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
            if category in self.profile.get('skills', {}):
                skills.extend(self.profile['skills'][category])
        
        return skills[:10]  # Limit to top 10 skills
    
    def get_job_requirements(self, job_category: str) -> str:
        """Get typical job requirements for a category"""
        requirements = {
            'data_engineer': 'Data pipeline development, ETL/ELT processes, database management, cloud platforms, big data technologies',
            'data_analyst': 'Data analysis, statistical analysis, data visualization, SQL, analytics tools',
            'ai_engineer': 'Machine learning, deep learning, model development, MLOps, AI/ML frameworks',
            'bi_developer': 'Business intelligence tools, dashboard development, data modeling, SQL, KPI tracking',
            'ai_prototyper': 'Rapid prototyping, proof of concepts, user experience design, AI/ML integration'
        }
        
        return requirements.get(job_category, 'General technical skills')
    
    def format_experience_for_resume(self) -> str:
        """Format experience for resume generation"""
        experience_text = ""
        for exp in self.profile.get('experience', []):
            experience_text += f"{exp['position']} at {exp['company']} ({exp['period']}): {exp['details']}\n"
        return experience_text
    
    def get_fallback_resume(self) -> str:
        """Get a fallback resume if AI generation fails"""
        return """
        [Your Name]
        [Your Email] | [Your Phone] | [Your Location]
        
        PROFESSIONAL SUMMARY
        Experienced data professional with expertise in data engineering, analysis, and AI development.
        
        SKILLS
        [List your actual skills here]
        
        EXPERIENCE
        [List your actual experience here]
        
        EDUCATION
        [Your education details]
        """
    
    def generate_cover_letter(self, job_info: Dict) -> str:
        """Generate a heartfelt cover letter for the job"""
        try:
            company = job_info['company']
            position = job_info['title']
            
            # Get detailed job information
            job_description = job_info.get('description', '')
            job_requirements = job_info.get('requirements', [])
            company_info = job_info.get('company_info', {})
            job_details = job_info.get('job_details', {})
            
            # Get personal notes from profile
            personal_notes = self.profile.get('personal_notes', '')
            
            prompt = f"""
            Create a heartfelt and genuine cover letter for a {position} position at {company}.
            
            JOB DETAILS:
            - Position: {position}
            - Company: {company}
            - Company Size: {company_info.get('size', 'Not specified')}
            - Industry: {company_info.get('industry', 'Not specified')}
            - Experience Level: {job_details.get('seniority level', 'Not specified')}
            
            JOB DESCRIPTION:
            {job_description[:1500] if job_description else 'No detailed description available'}
            
            SPECIFIC JOB REQUIREMENTS:
            {chr(10).join([f"- {req}" for req in job_requirements[:10]]) if job_requirements else 'No specific requirements listed'}
            
            PERSONAL CONTEXT FROM CANDIDATE:
            {personal_notes}
            
            COVER LETTER REQUIREMENTS:
            1. Make it personal and genuine - not generic
            2. Reference specific aspects of the job description that excite you
            3. Explain why the candidate is excited about this specific role and company
            4. Connect the candidate's background to the specific role requirements
            5. Show you've read and understood the job description
            6. Keep it honest and authentic
            7. Show enthusiasm and passion for the specific role
            8. Keep it to 2-3 paragraphs maximum
            9. Make it specific to this company and role
            10. Address how the candidate's skills align with the job requirements
            11. Show understanding of the company's industry and challenges
            12. End with a specific call to action
            
            Generate a compelling cover letter that shows genuine interest in this specific role and demonstrates understanding of the company's needs.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert cover letter writer who creates genuine, heartfelt, and compelling cover letters. You analyze job descriptions in detail and create personalized letters that show deep understanding of the role and company."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.8
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate cover letter: {e}")
            return self.get_fallback_cover_letter(job_info)
    
    def get_fallback_cover_letter(self, job_info: Dict) -> str:
        """Get a fallback cover letter if AI generation fails"""
        return f"""
        Dear Hiring Manager,
        
        I am writing to express my strong interest in the {job_info['title']} position at {job_info['company']}. 
        With my background in data and AI, I am excited about the opportunity to contribute to your team.
        
        [Your personal story and why you're interested in this role]
        
        I look forward to discussing how my skills and experience can benefit {job_info['company']}.
        
        Best regards,
        [Your Name]
        """
    
    def apply_to_job(self, job_info: Dict) -> bool:
        """Apply to a specific job"""
        try:
            logger.info(f"Applying to {job_info['title']} at {job_info['company']}")
            
            # Navigate to job page
            self.driver.get(job_info['job_url'])
            self.human_delay(3, 6)
            
            # Look for apply button
            try:
                apply_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-control-name='jobdetails_topcard_inapply']"))
                )
                apply_button.click()
                self.human_delay(2, 4)
                
                # Handle application form
                success = self.handle_application_form(job_info)
                
                if success:
                    self.jobs_applied.append(job_info)
                    logger.info(f"Successfully applied to {job_info['title']} at {job_info['company']}")
                    return True
                else:
                    logger.warning(f"Failed to complete application for {job_info['title']}")
                    return False
                    
            except TimeoutException:
                logger.warning(f"Apply button not found for {job_info['title']}")
                return False
                
        except Exception as e:
            logger.error(f"Application failed for {job_info['title']}: {e}")
            return False
    
    def handle_application_form(self, job_info: Dict) -> bool:
        """Handle the job application form"""
        try:
            # Generate customized resume and cover letter
            resume = self.generate_customized_resume(job_info)
            cover_letter = self.generate_cover_letter(job_info)
            
            # Look for form fields and fill them
            # This is a simplified version - actual implementation would need to handle various form layouts
            
            # Try to find and fill resume upload
            try:
                resume_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                # For now, we'll just note that we have the resume content
                logger.info("Resume content generated and ready")
            except NoSuchElementException:
                logger.info("No file upload field found")
            
            # Try to find and fill cover letter field
            try:
                cover_letter_field = self.driver.find_element(By.CSS_SELECTOR, "textarea[name*='cover'], textarea[name*='letter']")
                self.human_type(cover_letter_field, cover_letter)
                logger.info("Cover letter filled")
            except NoSuchElementException:
                logger.info("No cover letter field found")
            
            # Submit application
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button[data-control-name*='submit']")
                submit_button.click()
                self.human_delay(3, 6)
                
                # Check if application was successful
                success_indicators = [
                    "Application submitted",
                    "Thank you for your application",
                    "Application received"
                ]
                
                page_text = self.driver.page_source.lower()
                if any(indicator.lower() in page_text for indicator in success_indicators):
                    return True
                else:
                    return False
                    
            except NoSuchElementException:
                logger.warning("Submit button not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to handle application form: {e}")
            return False
    
    def reach_out_to_hiring_managers(self, job_info: Dict):
        """Attempt to reach out to hiring managers on LinkedIn"""
        try:
            # This would require additional LinkedIn automation
            # For now, we'll just log the intention
            logger.info(f"Would reach out to hiring managers for {job_info['title']} at {job_info['company']}")
            
            # In a full implementation, this would:
            # 1. Search for company employees on LinkedIn
            # 2. Identify hiring managers/recruiters
            # 3. Send personalized connection requests
            # 4. Follow up with messages
            
        except Exception as e:
            logger.error(f"Failed to reach out to hiring managers: {e}")
    
    def human_delay(self, min_seconds: int = None, max_seconds: int = None):
        """Add human-like delays between actions"""
        if min_seconds is None:
            min_seconds = self.min_delay
        if max_seconds is None:
            max_seconds = self.max_delay
            
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def human_type(self, element, text: str):
        """Type text in a human-like manner"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def take_break(self):
        """Take a human-like break"""
        break_duration = random.randint(*self.break_duration)
        logger.info(f"Taking a break for {break_duration} seconds...")
        time.sleep(break_duration)
    
    def run_job_search_session(self):
        """Run a complete job search and application session"""
        try:
            logger.info("Starting LinkedIn job search session")
            
            # Setup and login
            self.setup_driver()
            self.login_to_linkedin()
            
            # Search for jobs in each location
            all_jobs = []
            for location in self.config['job_search']['locations']:
                for keyword in self.config['job_search']['keywords']:
                    jobs = self.search_jobs(keyword, location)
                    all_jobs.extend(jobs)
                    self.human_delay(5, 10)  # Delay between searches
            
            # Remove duplicates and sort by relevance
            unique_jobs = self.remove_duplicate_jobs(all_jobs)
            sorted_jobs = self.sort_jobs_by_relevance(unique_jobs)
            
            logger.info(f"Found {len(sorted_jobs)} unique suitable jobs")
            
            # Apply to jobs
            applications_count = 0
            max_applications = self.config['job_search']['max_applications_per_session']
            
            for job in sorted_jobs:
                if applications_count >= max_applications:
                    break
                
                # Take breaks to look human
                if applications_count > 0 and applications_count % self.break_interval == 0:
                    self.take_break()
                
                # Apply to job
                if self.apply_to_job(job):
                    applications_count += 1
                    
                    # Try to reach out to hiring managers
                    if random.random() < 0.3:  # 30% chance
                        self.reach_out_to_hiring_managers(job)
                    
                    # Human-like delay between applications
                    self.human_delay(
                        self.config['job_search']['min_delay_between_applications'],
                        self.config['job_search']['max_delay_between_applications']
                    )
                
                # Random longer breaks occasionally
                if random.random() < 0.1:  # 10% chance
                    self.human_delay(15, 30)
            
            logger.info(f"Session completed. Applied to {applications_count} jobs.")
            self.save_session_results()
            
        except Exception as e:
            logger.error(f"Job search session failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()
    
    def remove_duplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on job ID"""
        seen_ids = set()
        unique_jobs = []
        
        for job in jobs:
            if job['job_id'] not in seen_ids:
                seen_ids.add(job['job_id'])
                unique_jobs.append(job)
        
        return unique_jobs
    
    def sort_jobs_by_relevance(self, jobs: List[Dict]) -> List[Dict]:
        """Sort jobs by relevance score"""
        for job in jobs:
            job['relevance_score'] = self.calculate_relevance_score(job)
        
        return sorted(jobs, key=lambda x: x['relevance_score'], reverse=True)
    
    def calculate_relevance_score(self, job: Dict) -> float:
        """Calculate relevance score for a job"""
        score = 0.0
        
        # Location preference
        if 'singapore' in job['location'].lower():
            score += 10.0
        elif 'hong kong' in job['location'].lower():
            score += 8.0
        
        # Job category match
        if job['keyword_matched'] != 'general':
            score += 5.0
        
        # Company size preference (could be enhanced)
        score += random.uniform(0, 2)  # Small random factor
        
        return score
    
    def save_session_results(self):
        """Save session results to file"""
        results = {
            'session_date': self.session_start.isoformat(),
            'jobs_applied': self.jobs_applied,
            'total_applications': len(self.jobs_applied),
            'session_duration': str(datetime.now() - self.session_start)
        }
        
        with open(f'session_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as file:
            json.dump(results, file, indent=2)
        
        logger.info("Session results saved")

def main():
    """Main function to run the LinkedIn job agent"""
    try:
        agent = LinkedInJobAgent()
        agent.run_job_search_session()
    except KeyboardInterrupt:
        logger.info("Session interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()