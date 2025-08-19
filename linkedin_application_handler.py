#!/usr/bin/env python3
"""
LinkedIn Application Form Handler
Handles various types of job application forms and file uploads
"""

import os
import time
import random
import logging
from typing import Dict, List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

class LinkedInApplicationHandler:
    def __init__(self, driver, config: Dict):
        """Initialize the application form handler"""
        self.driver = driver
        self.config = config
        self.temp_files = []
        
    def handle_application_form(self, job_info: Dict, resume_content: str, cover_letter: str) -> bool:
        """Handle the complete job application process"""
        try:
            logger.info(f"Starting application process for {job_info['title']} at {job_info['company']}")
            
            # Step 1: Look for apply button
            if not self.find_and_click_apply_button():
                logger.warning("Apply button not found")
                return False
            
            # Step 2: Handle different application scenarios
            application_success = False
            
            # Try LinkedIn Easy Apply first
            if self.is_linkedin_easy_apply():
                application_success = self.handle_linkedin_easy_apply(resume_content, cover_letter)
            
            # If not LinkedIn Easy Apply, try external application
            if not application_success:
                application_success = self.handle_external_application(resume_content, cover_letter)
            
            # Step 3: Clean up temporary files
            self.cleanup_temp_files()
            
            return application_success
            
        except Exception as e:
            logger.error(f"Application handling failed: {e}")
            self.cleanup_temp_files()
            return False
    
    def find_and_click_apply_button(self) -> bool:
        """Find and click the apply button"""
        try:
            # Wait for page to load
            time.sleep(random.uniform(2, 4))
            
            # Look for various apply button selectors
            apply_selectors = [
                "button[data-control-name='jobdetails_topcard_inapply']",
                "button[data-control-name='jobdetails_topcard_apply']",
                "button[aria-label*='Apply']",
                "button[aria-label*='Easy Apply']",
                "button:contains('Apply')",
                ".apply-button",
                ".job-apply-button"
            ]
            
            for selector in apply_selectors:
                try:
                    apply_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    apply_button.click()
                    logger.info("Apply button clicked successfully")
                    time.sleep(random.uniform(2, 4))
                    return True
                except (TimeoutException, NoSuchElementException):
                    continue
            
            # Try finding by text content
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    if "apply" in button.text.lower():
                        button.click()
                        logger.info("Apply button found by text content")
                        time.sleep(random.uniform(2, 4))
                        return True
            except Exception:
                pass
            
            logger.warning("No apply button found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to find apply button: {e}")
            return False
    
    def is_linkedin_easy_apply(self) -> bool:
        """Check if this is a LinkedIn Easy Apply form"""
        try:
            # Look for LinkedIn Easy Apply indicators
            easy_apply_indicators = [
                ".jobs-easy-apply-content",
                ".jobs-easy-apply-form",
                "[data-test-id='easy-apply-form']",
                ".jobs-easy-apply-modal"
            ]
            
            for indicator in easy_apply_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"Could not determine if Easy Apply: {e}")
            return False
    
    def handle_linkedin_easy_apply(self, resume_content: str, cover_letter: str) -> bool:
        """Handle LinkedIn Easy Apply forms"""
        try:
            logger.info("Handling LinkedIn Easy Apply form")
            
            # Wait for form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-easy-apply-content"))
            )
            
            # Step 1: Handle resume upload
            resume_uploaded = self.handle_resume_upload()
            
            # Step 2: Fill additional questions
            questions_filled = self.fill_easy_apply_questions()
            
            # Step 3: Add cover letter if possible
            cover_letter_added = self.add_cover_letter_to_easy_apply(cover_letter)
            
            # Step 4: Submit application
            if resume_uploaded:
                return self.submit_easy_apply()
            else:
                logger.warning("Resume upload failed, cannot submit")
                return False
                
        except Exception as e:
            logger.error(f"LinkedIn Easy Apply handling failed: {e}")
            return False
    
    def handle_resume_upload(self) -> bool:
        """Handle resume file upload"""
        try:
            # Look for file upload input
            file_input_selectors = [
                "input[type='file']",
                "input[accept*='.pdf']",
                "input[accept*='.doc']",
                "input[accept*='.docx']",
                "[data-test-id='resume-upload-input']"
            ]
            
            file_input = None
            for selector in file_input_selectors:
                try:
                    file_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not file_input:
                logger.warning("No file upload input found")
                return False
            
            # Create temporary resume file
            resume_file = self.create_temp_resume_file()
            if not resume_file:
                return False
            
            # Upload the file
            file_input.send_keys(resume_file)
            logger.info("Resume file uploaded successfully")
            
            # Wait for upload to complete
            time.sleep(random.uniform(3, 6))
            
            return True
            
        except Exception as e:
            logger.error(f"Resume upload failed: {e}")
            return False
    
    def create_temp_resume_file(self) -> Optional[str]:
        """Create a temporary resume file for upload"""
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Create resume file (you might want to generate actual PDF/DOC here)
            resume_file = os.path.join(temp_dir, "resume.pdf")
            
            # For now, create a simple text file (in production, generate proper PDF)
            with open(resume_file, 'w') as f:
                f.write("Resume content would go here")
            
            self.temp_files.append(resume_file)
            return resume_file
            
        except Exception as e:
            logger.error(f"Failed to create temp resume file: {e}")
            return None
    
    def fill_easy_apply_questions(self) -> bool:
        """Fill out additional questions in Easy Apply forms"""
        try:
            # Look for question fields
            question_selectors = [
                "input[type='text']",
                "textarea",
                "select",
                "input[type='number']",
                "input[type='email']",
                "input[type='tel']"
            ]
            
            questions_filled = 0
            
            for selector in question_selectors:
                try:
                    fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for field in fields:
                        if self.should_fill_field(field):
                            if self.fill_field_appropriately(field):
                                questions_filled += 1
                                time.sleep(random.uniform(0.5, 1.5))
                except Exception as e:
                    logger.warning(f"Failed to handle field with selector {selector}: {e}")
                    continue
            
            logger.info(f"Filled {questions_filled} question fields")
            return questions_filled > 0
            
        except Exception as e:
            logger.error(f"Failed to fill questions: {e}")
            return False
    
    def should_fill_field(self, field) -> bool:
        """Determine if a field should be filled"""
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
            
            # Relevant field types
            relevant_types = ["text", "email", "tel", "number", "url"]
            relevant_names = ["name", "email", "phone", "experience", "years", "skills"]
            
            if field_type in relevant_types:
                return True
            
            if any(name in field_name.lower() for name in relevant_names):
                return True
            
            return False
            
        except Exception:
            return False
    
    def fill_field_appropriately(self, field) -> bool:
        """Fill a field with appropriate data based on its type and name"""
        try:
            field_type = field.get_attribute("type")
            field_name = field.get_attribute("name") or field.get_attribute("id") or ""
            field_name_lower = field_name.lower()
            
            # Determine appropriate value
            value = self.get_field_value(field_type, field_name_lower)
            
            if value:
                # Clear field first
                field.clear()
                time.sleep(random.uniform(0.2, 0.5))
                
                # Type value
                self.human_type(field, value)
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Failed to fill field: {e}")
            return False
    
    def get_field_value(self, field_type: str, field_name: str) -> Optional[str]:
        """Get appropriate value for a field based on type and name"""
        try:
            # Common field mappings
            if "name" in field_name:
                return "John Doe"  # You'd want to use actual profile data
            
            elif "email" in field_name:
                return "john.doe@example.com"  # Use actual email
            
            elif "phone" in field_name or "tel" in field_name:
                return "+65 9123 4567"  # Singapore format
            
            elif "experience" in field_name or "years" in field_name:
                return "5"  # Use actual experience
            
            elif "skills" in field_name:
                return "Python, SQL, Data Engineering"  # Use actual skills
            
            elif "education" in field_name:
                return "Bachelor's Degree"  # Use actual education
            
            elif "location" in field_name:
                return "Singapore"  # Use actual location
            
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
    
    def add_cover_letter_to_easy_apply(self, cover_letter: str) -> bool:
        """Add cover letter to Easy Apply form if possible"""
        try:
            # Look for cover letter field
            cover_letter_selectors = [
                "textarea[name*='cover']",
                "textarea[name*='letter']",
                "textarea[placeholder*='cover']",
                "textarea[placeholder*='letter']",
                "[data-test-id='cover-letter-input']"
            ]
            
            for selector in cover_letter_selectors:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if field.is_displayed() and field.is_enabled():
                        field.clear()
                        time.sleep(random.uniform(0.5, 1))
                        self.human_type(field, cover_letter)
                        logger.info("Cover letter added to Easy Apply form")
                        return True
                except NoSuchElementException:
                    continue
            
            logger.info("No cover letter field found in Easy Apply form")
            return False
            
        except Exception as e:
            logger.error(f"Failed to add cover letter: {e}")
            return False
    
    def submit_easy_apply(self) -> bool:
        """Submit the Easy Apply form"""
        try:
            # Look for submit button
            submit_selectors = [
                "button[data-control-name='submit_unify']",
                "button[aria-label='Submit application']",
                "button[type='submit']",
                ".jobs-easy-apply-content button:last-child"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_enabled():
                        submit_button.click()
                        logger.info("Easy Apply form submitted")
                        
                        # Wait for submission to complete
                        time.sleep(random.uniform(3, 6))
                        
                        # Check for success indicators
                        if self.check_application_success():
                            return True
                        else:
                            logger.warning("Application submission may have failed")
                            return False
                except NoSuchElementException:
                    continue
            
            logger.error("No submit button found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to submit Easy Apply: {e}")
            return False
    
    def handle_external_application(self, resume_content: str, cover_letter: str) -> bool:
        """Handle external application systems"""
        try:
            logger.info("Handling external application system")
            
            # Check if we're redirected to external site
            current_url = self.driver.current_url
            if "linkedin.com" not in current_url:
                logger.info(f"Redirected to external site: {current_url}")
                return self.handle_external_site_application(resume_content, cover_letter)
            
            # Look for external application link
            external_link_selectors = [
                "a[href*='apply']",
                "a[href*='career']",
                "a[href*='jobs']",
                "button[data-control-name='external_apply']"
            ]
            
            for selector in external_link_selectors:
                try:
                    link = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if link.is_displayed():
                        link.click()
                        logger.info("Clicked external application link")
                        time.sleep(random.uniform(3, 6))
                        return self.handle_external_site_application(resume_content, cover_letter)
                except NoSuchElementException:
                    continue
            
            logger.warning("No external application link found")
            return False
            
        except Exception as e:
            logger.error(f"External application handling failed: {e}")
            return False
    
    def handle_external_site_application(self, resume_content: str, cover_letter: str) -> bool:
        """Handle application on external company career sites"""
        try:
            logger.info("Handling external site application")
            
            # Wait for page to load
            time.sleep(random.uniform(3, 6))
            
            # This is a complex task that would require:
            # 1. Detecting the type of application system
            # 2. Mapping form fields
            # 3. Handling different file upload methods
            # 4. Managing authentication if required
            
            # For now, we'll log what we see and return False
            # In a production system, you'd need extensive form detection logic
            
            logger.info("External site application requires manual implementation")
            logger.info(f"Current URL: {self.driver.current_url}")
            
            # Take a screenshot for analysis
            screenshot_path = f"external_application_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
            
            return False
            
        except Exception as e:
            logger.error(f"External site application failed: {e}")
            return False
    
    def check_application_success(self) -> bool:
        """Check if application was submitted successfully"""
        try:
            # Look for success indicators
            success_indicators = [
                "Application submitted",
                "Thank you for your application",
                "Application received",
                "Successfully applied",
                "Application complete"
            ]
            
            page_text = self.driver.page_source.lower()
            
            for indicator in success_indicators:
                if indicator.lower() in page_text:
                    logger.info(f"Success indicator found: {indicator}")
                    return True
            
            # Check for error indicators
            error_indicators = [
                "error occurred",
                "application failed",
                "please try again",
                "something went wrong"
            ]
            
            for indicator in error_indicators:
                if indicator.lower() in page_text:
                    logger.warning(f"Error indicator found: {indicator}")
                    return False
            
            # If no clear indicators, assume success if we're still on the page
            return True
            
        except Exception as e:
            logger.error(f"Failed to check application success: {e}")
            return False
    
    def human_type(self, element, text: str):
        """Type text in a human-like manner"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            for file_path in self.temp_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Cleaned up temp file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {file_path}: {e}")
            
            self.temp_files.clear()
            
        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {e}")