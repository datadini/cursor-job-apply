#!/usr/bin/env python3
"""
External Form Mapper
Maps and handles various types of job application forms on company career sites
"""

import time
import random
import logging
from typing import Dict, List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

logger = logging.getLogger(__name__)

class ExternalFormMapper:
    def __init__(self, driver, config: Dict):
        """Initialize the external form mapper"""
        self.driver = driver
        self.config = config
        self.form_patterns = self.load_form_patterns()
        
    def load_form_patterns(self) -> Dict:
        """Load common form patterns for different application systems"""
        return {
            'workday': {
                'name': 'Workday',
                'selectors': {
                    'name_fields': ['input[name*="name"]', 'input[id*="name"]'],
                    'email_fields': ['input[type="email"]', 'input[name*="email"]'],
                    'phone_fields': ['input[type="tel"]', 'input[name*="phone"]'],
                    'resume_upload': ['input[type="file"]', 'input[accept*=".pdf"]'],
                    'submit_button': ['button[type="submit"]', 'input[type="submit"]']
                }
            },
            'lever': {
                'name': 'Lever',
                'selectors': {
                    'name_fields': ['input[name="name"]', 'input[name="full_name"]'],
                    'email_fields': ['input[name="email"]', 'input[type="email"]'],
                    'phone_fields': ['input[name="phone"]', 'input[type="tel"]'],
                    'resume_upload': ['input[type="file"]', 'input[accept*=".pdf"]'],
                    'submit_button': ['button[type="submit"]', 'input[type="submit"]']
                }
            },
            'greenhouse': {
                'name': 'Greenhouse',
                'selectors': {
                    'name_fields': ['input[name="name"]', 'input[name="full_name"]'],
                    'email_fields': ['input[name="email"]', 'input[type="email"]'],
                    'phone_fields': ['input[name="phone"]', 'input[type="tel"]'],
                    'resume_upload': ['input[type="file"]', 'input[accept*=".pdf"]'],
                    'submit_button': ['button[type="submit"]', 'input[type="submit"]']
                }
            },
            'bamboo': {
                'name': 'BambooHR',
                'selectors': {
                    'name_fields': ['input[name="name"]', 'input[name="full_name"]'],
                    'email_fields': ['input[name="email"]', 'input[type="email"]'],
                    'phone_fields': ['input[name="phone"]', 'input[type="tel"]'],
                    'resume_upload': ['input[type="file"]', 'input[accept*=".pdf"]'],
                    'submit_button': ['button[type="submit"]', 'input[type="submit"]']
                }
            },
            'generic': {
                'name': 'Generic Form',
                'selectors': {
                    'name_fields': ['input[name*="name"]', 'input[id*="name"]', 'input[placeholder*="name"]'],
                    'email_fields': ['input[type="email"]', 'input[name*="email"]', 'input[placeholder*="email"]'],
                    'phone_fields': ['input[type="tel"]', 'input[name*="phone"]', 'input[placeholder*="phone"]'],
                    'resume_upload': ['input[type="file"]', 'input[accept*=".pdf"]', 'input[accept*=".doc"]'],
                    'submit_button': ['button[type="submit"]', 'input[type="submit"]', 'button:contains("Submit")']
                }
            }
        }
    
    def detect_application_system(self) -> str:
        """Detect which application system is being used"""
        try:
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            # Check URL patterns
            if 'workday' in current_url:
                return 'workday'
            elif 'lever' in current_url:
                return 'lever'
            elif 'greenhouse' in current_url:
                return 'greenhouse'
            elif 'bamboo' in current_url:
                return 'bamboo'
            
            # Check page source for system indicators
            if 'workday' in page_source:
                return 'workday'
            elif 'lever' in page_source:
                return 'lever'
            elif 'greenhouse' in page_source:
                return 'greenhouse'
            elif 'bamboo' in page_source:
                return 'bamboo'
            
            # Check for common form patterns
            if self.detect_form_patterns():
                return 'generic'
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"Failed to detect application system: {e}")
            return 'unknown'
    
    def detect_form_patterns(self) -> bool:
        """Detect if this looks like a job application form"""
        try:
            # Look for common form indicators
            form_indicators = [
                'form',
                'application',
                'apply',
                'submit',
                'upload',
                'resume',
                'cover letter'
            ]
            
            page_text = self.driver.page_source.lower()
            form_count = sum(1 for indicator in form_indicators if indicator in page_text)
            
            # Also check for actual form elements
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            
            return form_count >= 3 or len(forms) > 0 or len(inputs) > 5
            
        except Exception as e:
            logger.error(f"Failed to detect form patterns: {e}")
            return False
    
    def map_form_fields(self, system_type: str) -> Dict:
        """Map form fields for the detected system"""
        try:
            if system_type not in self.form_patterns:
                system_type = 'generic'
            
            patterns = self.form_patterns[system_type]
            mapped_fields = {}
            
            # Map each field type
            for field_type, selectors in patterns['selectors'].items():
                mapped_fields[field_type] = self.find_fields_by_selectors(selectors)
            
            logger.info(f"Mapped {len(mapped_fields)} field types for {patterns['name']}")
            return mapped_fields
            
        except Exception as e:
            logger.error(f"Failed to map form fields: {e}")
            return {}
    
    def find_fields_by_selectors(self, selectors: List[str]) -> List:
        """Find form fields using multiple selectors"""
        fields = []
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        fields.append(element)
            except Exception as e:
                logger.warning(f"Failed to find fields with selector {selector}: {e}")
                continue
        
        return fields
    
    def fill_application_form(self, mapped_fields: Dict, profile_data: Dict, resume_file: str, cover_letter: str) -> bool:
        """Fill out the application form with provided data"""
        try:
            logger.info("Starting to fill application form")
            
            # Fill basic information
            self.fill_basic_fields(mapped_fields, profile_data)
            
            # Handle resume upload
            resume_uploaded = self.handle_resume_upload(mapped_fields.get('resume_upload', []), resume_file)
            
            # Fill additional questions
            questions_filled = self.fill_additional_questions(mapped_fields)
            
            # Add cover letter if possible
            cover_letter_added = self.add_cover_letter(mapped_fields, cover_letter)
            
            # Submit the form
            if resume_uploaded:
                return self.submit_form(mapped_fields.get('submit_button', []))
            else:
                logger.warning("Resume upload failed, cannot submit")
                return False
                
        except Exception as e:
            logger.error(f"Failed to fill application form: {e}")
            return False
    
    def fill_basic_fields(self, mapped_fields: Dict, profile_data: Dict):
        """Fill basic information fields"""
        try:
            # Fill name fields
            name_fields = mapped_fields.get('name_fields', [])
            for field in name_fields:
                if not field.get_attribute("value"):
                    self.fill_field_appropriately(field, "name", profile_data)
                    break
            
            # Fill email fields
            email_fields = mapped_fields.get('email_fields', [])
            for field in email_fields:
                if not field.get_attribute("value"):
                    self.fill_field_appropriately(field, "email", profile_data)
                    break
            
            # Fill phone fields
            phone_fields = mapped_fields.get('phone_fields', [])
            for field in phone_fields:
                if not field.get_attribute("value"):
                    self.fill_field_appropriately(field, "phone", profile_data)
                    break
            
            logger.info("Basic fields filled")
            
        except Exception as e:
            logger.error(f"Failed to fill basic fields: {e}")
    
    def fill_field_appropriately(self, field, field_type: str, profile_data: Dict):
        """Fill a field with appropriate data"""
        try:
            value = self.get_field_value(field_type, profile_data)
            
            if value:
                # Clear field first
                field.clear()
                time.sleep(random.uniform(0.2, 0.5))
                
                # Type value
                self.human_type(field, value)
                time.sleep(random.uniform(0.5, 1))
                
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Failed to fill field: {e}")
            return False
    
    def get_field_value(self, field_type: str, profile_data: Dict) -> Optional[str]:
        """Get appropriate value for a field type"""
        try:
            if field_type == "name":
                return profile_data.get('name', 'John Doe')
            elif field_type == "email":
                return profile_data.get('email', 'john.doe@example.com')
            elif field_type == "phone":
                return profile_data.get('phone', '+65 9123 4567')
            elif field_type == "experience":
                return str(profile_data.get('years_experience', '5'))
            elif field_type == "location":
                return profile_data.get('location', 'Singapore')
            else:
                return None
                
        except Exception:
            return None
    
    def handle_resume_upload(self, resume_fields: List, resume_file: str) -> bool:
        """Handle resume file upload"""
        try:
            if not resume_fields:
                logger.warning("No resume upload fields found")
                return False
            
            # Use the first available resume upload field
            resume_field = resume_fields[0]
            
            # Upload the file
            resume_field.send_keys(resume_file)
            logger.info("Resume file uploaded")
            
            # Wait for upload to complete
            time.sleep(random.uniform(3, 6))
            
            return True
            
        except Exception as e:
            logger.error(f"Resume upload failed: {e}")
            return False
    
    def fill_additional_questions(self, mapped_fields: Dict) -> int:
        """Fill additional question fields"""
        try:
            # Look for additional input fields
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            all_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            all_selects = self.driver.find_elements(By.TAG_NAME, "select")
            
            questions_filled = 0
            
            # Process text inputs
            for field in all_inputs:
                if self.should_fill_additional_field(field):
                    if self.fill_additional_field(field):
                        questions_filled += 1
            
            # Process textareas
            for field in all_textareas:
                if self.should_fill_additional_field(field):
                    if self.fill_additional_field(field):
                        questions_filled += 1
            
            # Process select dropdowns
            for field in all_selects:
                if self.should_fill_additional_field(field):
                    if self.fill_select_field(field):
                        questions_filled += 1
            
            logger.info(f"Filled {questions_filled} additional questions")
            return questions_filled
            
        except Exception as e:
            logger.error(f"Failed to fill additional questions: {e}")
            return 0
    
    def should_fill_additional_field(self, field) -> bool:
        """Determine if an additional field should be filled"""
        try:
            # Check if field is visible and enabled
            if not field.is_displayed() or not field.is_enabled():
                return False
            
            # Check if field already has a value
            if field.get_attribute("value"):
                return False
            
            # Check if field is required
            required = field.get_attribute("required") or field.get_attribute("aria-required")
            if required:
                return True
            
            # Check field type and name for relevance
            field_type = field.get_attribute("type")
            field_name = field.get_attribute("name") or field.get_attribute("id") or ""
            field_placeholder = field.get_attribute("placeholder") or ""
            
            # Relevant field types
            relevant_types = ["text", "email", "tel", "number", "url"]
            relevant_names = ["experience", "years", "skills", "education", "location", "salary", "availability"]
            
            if field_type in relevant_types:
                return True
            
            if any(name in field_name.lower() for name in relevant_names):
                return True
            
            if any(name in field_placeholder.lower() for name in relevant_names):
                return True
            
            return False
            
        except Exception:
            return False
    
    def fill_additional_field(self, field) -> bool:
        """Fill an additional field with appropriate data"""
        try:
            field_type = field.get_attribute("type")
            field_name = field.get_attribute("name") or field.get_attribute("id") or ""
            field_placeholder = field.get_attribute("placeholder") or ""
            
            # Determine appropriate value
            value = self.get_additional_field_value(field_type, field_name, field_placeholder)
            
            if value:
                # Clear field first
                field.clear()
                time.sleep(random.uniform(0.2, 0.5))
                
                # Type value
                self.human_type(field, value)
                time.sleep(random.uniform(0.5, 1))
                
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Failed to fill additional field: {e}")
            return False
    
    def get_additional_field_value(self, field_type: str, field_name: str, field_placeholder: str) -> Optional[str]:
        """Get appropriate value for an additional field"""
        try:
            field_text = (field_name + " " + field_placeholder).lower()
            
            # Common field mappings
            if any(word in field_text for word in ["experience", "years"]):
                return "5"
            
            elif any(word in field_text for word in ["skills", "technologies"]):
                return "Python, SQL, Data Engineering, AWS, Apache Spark"
            
            elif any(word in field_text for word in ["education", "degree"]):
                return "Bachelor's Degree in Computer Science"
            
            elif any(word in field_text for word in ["location", "city"]):
                return "Singapore"
            
            elif any(word in field_text for word in ["salary", "compensation"]):
                return "Negotiable"
            
            elif any(word in field_text for word in ["availability", "start date"]):
                return "Immediate"
            
            elif any(word in field_text for word in ["portfolio", "github", "website"]):
                return "https://github.com/username"
            
            # Default values based on field type
            elif field_type == "text":
                return "See resume for details"
            
            elif field_type == "number":
                return "5"
            
            elif field_type == "email":
                return "john.doe@example.com"
            
            return None
            
        except Exception:
            return None
    
    def fill_select_field(self, field) -> bool:
        """Fill a select dropdown field"""
        try:
            select = Select(field)
            options = select.options
            
            if len(options) > 1:
                # Try to find the most appropriate option
                for option in options:
                    option_text = option.text.lower()
                    if any(word in option_text for word in ["yes", "available", "immediate", "bachelor", "5+"]):
                        select.select_by_visible_text(option.text)
                        time.sleep(random.uniform(0.5, 1))
                        return True
                
                # If no specific option found, select the second option (usually not the first which might be "Select...")
                if len(options) > 1:
                    select.select_by_index(1)
                    time.sleep(random.uniform(0.5, 1))
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Failed to fill select field: {e}")
            return False
    
    def add_cover_letter(self, mapped_fields: Dict, cover_letter: str) -> bool:
        """Add cover letter to the form if possible"""
        try:
            # Look for cover letter fields
            cover_letter_selectors = [
                'textarea[name*="cover"]',
                'textarea[name*="letter"]',
                'textarea[placeholder*="cover"]',
                'textarea[placeholder*="letter"]',
                'textarea[name*="message"]',
                'textarea[name*="additional"]'
            ]
            
            for selector in cover_letter_selectors:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if field.is_displayed() and field.is_enabled():
                        field.clear()
                        time.sleep(random.uniform(0.5, 1))
                        self.human_type(field, cover_letter)
                        logger.info("Cover letter added to form")
                        return True
                except NoSuchElementException:
                    continue
            
            logger.info("No cover letter field found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to add cover letter: {e}")
            return False
    
    def submit_form(self, submit_fields: List) -> bool:
        """Submit the application form"""
        try:
            if not submit_fields:
                logger.warning("No submit button found")
                return False
            
            # Try to find and click submit button
            for submit_field in submit_fields:
                try:
                    if submit_field.is_enabled():
                        submit_field.click()
                        logger.info("Form submitted")
                        
                        # Wait for submission to complete
                        time.sleep(random.uniform(3, 6))
                        
                        # Check for success indicators
                        if self.check_submission_success():
                            return True
                        else:
                            logger.warning("Form submission may have failed")
                            return False
                except Exception as e:
                    logger.warning(f"Failed to click submit button: {e}")
                    continue
            
            logger.error("No working submit button found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to submit form: {e}")
            return False
    
    def check_submission_success(self) -> bool:
        """Check if form submission was successful"""
        try:
            # Look for success indicators
            success_indicators = [
                "thank you",
                "application submitted",
                "application received",
                "successfully applied",
                "application complete",
                "confirmation"
            ]
            
            page_text = self.driver.page_source.lower()
            
            for indicator in success_indicators:
                if indicator in page_text:
                    logger.info(f"Success indicator found: {indicator}")
                    return True
            
            # Check for error indicators
            error_indicators = [
                "error occurred",
                "application failed",
                "please try again",
                "something went wrong",
                "validation error"
            ]
            
            for indicator in error_indicators:
                if indicator in page_text:
                    logger.warning(f"Error indicator found: {indicator}")
                    return False
            
            # If no clear indicators, assume success if we're still on the page
            return True
            
        except Exception as e:
            logger.error(f"Failed to check submission success: {e}")
            return False
    
    def human_type(self, element, text: str):
        """Type text in a human-like manner"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))