#!/usr/bin/env python3
"""
LinkedIn Outreach Agent
Handles connecting with hiring managers and sending personalized messages
"""

import time
import random
import logging
from typing import Dict, List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class LinkedInOutreachAgent:
    def __init__(self, driver, config: Dict):
        """Initialize the outreach agent"""
        self.driver = driver
        self.config = config
        self.connections_sent = []
        self.messages_sent = []
        
    def find_hiring_managers(self, company_name: str, job_title: str) -> List[Dict]:
        """Find potential hiring managers at a company"""
        try:
            logger.info(f"Searching for hiring managers at {company_name}")
            
            # Search for company employees
            search_url = f"https://www.linkedin.com/search/results/people/?company={company_name}&title={job_title}"
            self.driver.get(search_url)
            time.sleep(random.uniform(3, 6))
            
            hiring_managers = []
            
            # Look for people with relevant titles
            relevant_titles = [
                'hiring manager', 'recruiter', 'talent acquisition', 'hr manager',
                'senior manager', 'director', 'head of', 'lead', 'principal'
            ]
            
            people_cards = self.driver.find_elements(By.CSS_SELECTOR, ".entity-result__item")
            
            for card in people_cards[:10]:  # Limit to first 10 results
                try:
                    name_element = card.find_element(By.CSS_SELECTOR, ".entity-result__title-text")
                    title_element = card.find_element(By.CSS_SELECTOR, ".entity-result__primary-subtitle")
                    
                    name = name_element.text.strip()
                    title = title_element.text.strip().lower()
                    
                    # Check if title is relevant
                    if any(keyword in title for keyword in relevant_titles):
                        profile_url = name_element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                        
                        hiring_managers.append({
                            'name': name,
                            'title': title,
                            'profile_url': profile_url,
                            'company': company_name
                        })
                        
                except Exception as e:
                    continue
            
            logger.info(f"Found {len(hiring_managers)} potential hiring managers")
            return hiring_managers
            
        except Exception as e:
            logger.error(f"Failed to find hiring managers: {e}")
            return []
    
    def send_connection_request(self, person: Dict, job_info: Dict) -> bool:
        """Send a personalized connection request"""
        try:
            logger.info(f"Sending connection request to {person['name']}")
            
            # Navigate to profile
            self.driver.get(person['profile_url'])
            time.sleep(random.uniform(2, 4))
            
            # Look for connect button
            try:
                connect_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Connect']"))
                )
                connect_button.click()
                time.sleep(random.uniform(1, 2))
                
                # Add personalized note if possible
                if self.config['outreach']['personalized_messages']:
                    note_added = self.add_connection_note(person, job_info)
                    if note_added:
                        logger.info("Added personalized note to connection request")
                
                # Send request
                send_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Send now']")
                send_button.click()
                time.sleep(random.uniform(2, 4))
                
                # Record the connection request
                self.connections_sent.append({
                    'person': person,
                    'job': job_info,
                    'timestamp': time.time(),
                    'type': 'connection_request'
                })
                
                logger.info(f"Connection request sent to {person['name']}")
                return True
                
            except TimeoutException:
                logger.warning(f"Connect button not found for {person['name']}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send connection request to {person['name']}: {e}")
            return False
    
    def add_connection_note(self, person: Dict, job_info: Dict) -> bool:
        """Add a personalized note to connection request"""
        try:
            # Look for "Add a note" button
            try:
                add_note_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Add a note']")
                add_note_button.click()
                time.sleep(random.uniform(1, 2))
                
                # Find note textarea
                note_field = self.driver.find_element(By.CSS_SELECTOR, "textarea[name='message']")
                
                # Generate personalized note
                note = self.generate_connection_note(person, job_info)
                
                # Type note
                self.human_type(note_field, note)
                time.sleep(random.uniform(1, 2))
                
                return True
                
            except NoSuchElementException:
                logger.info("No note option available for this connection request")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add connection note: {e}")
            return False
    
    def generate_connection_note(self, person: Dict, job_info: Dict) -> str:
        """Generate a personalized connection note"""
        try:
            # Use OpenAI to generate personalized note
            import openai
            
            prompt = f"""
            Create a brief, professional connection note for LinkedIn.
            
            Context:
            - Sending to: {person['name']} ({person['title']} at {person['company']})
            - Interested in: {job_info['title']} position
            - Company: {job_info['company']}
            
            Requirements:
            1. Keep it under 300 characters (LinkedIn limit)
            2. Be professional but warm
            3. Mention the specific role you're interested in
            4. Show you've done your research
            5. Ask to connect professionally
            
            Generate a compelling connection note.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional networking expert who writes compelling LinkedIn connection notes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate AI note: {e}")
            # Fallback note
            return f"Hi {person['name']}, I'm interested in the {job_info['title']} position at {job_info['company']}. Would love to connect and learn more about your team!"
    
    def send_follow_up_message(self, person: Dict, job_info: Dict) -> bool:
        """Send a follow-up message after connection"""
        try:
            logger.info(f"Sending follow-up message to {person['name']}")
            
            # Navigate to profile
            self.driver.get(person['profile_url'])
            time.sleep(random.uniform(2, 4))
            
            # Look for message button
            try:
                message_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Message']"))
                )
                message_button.click()
                time.sleep(random.uniform(1, 2))
                
                # Find message textarea
                message_field = self.driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='Write a message']")
                
                # Generate personalized message
                message = self.generate_follow_up_message(person, job_info)
                
                # Type message
                self.human_type(message_field, message)
                time.sleep(random.uniform(1, 2))
                
                # Send message
                send_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Send']")
                send_button.click()
                time.sleep(random.uniform(2, 4))
                
                # Record the message
                self.messages_sent.append({
                    'person': person,
                    'job': job_info,
                    'timestamp': time.time(),
                    'type': 'follow_up_message',
                    'content': message
                })
                
                logger.info(f"Follow-up message sent to {person['name']}")
                return True
                
            except TimeoutException:
                logger.warning(f"Message button not found for {person['name']}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send follow-up message to {person['name']}: {e}")
            return False
    
    def generate_follow_up_message(self, person: Dict, job_info: Dict) -> str:
        """Generate a personalized follow-up message"""
        try:
            # Use OpenAI to generate personalized message
            import openai
            
            prompt = f"""
            Create a professional follow-up message for LinkedIn.
            
            Context:
            - Sending to: {person['name']} ({person['title']} at {person['company']})
            - Interested in: {job_info['title']} position
            - Company: {job_info['company']}
            
            Requirements:
            1. Keep it professional and concise
            2. Reference the specific role
            3. Show enthusiasm for the company
            4. Ask a specific question or request
            5. Be respectful of their time
            
            Generate a compelling follow-up message.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional networking expert who writes compelling LinkedIn messages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate AI message: {e}")
            # Fallback message
            return f"""Hi {person['name']}, thank you for connecting!

I'm very interested in the {job_info['title']} position at {job_info['company']}. I'd love to learn more about the role and your team's work.

Would you be open to a brief conversation about the position? I'm particularly excited about {job_info['company']}'s mission and would love to understand how I could contribute.

Thanks for your time!"""
    
    def human_type(self, element, text: str):
        """Type text in a human-like manner"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def execute_outreach_strategy(self, job_info: Dict) -> Dict:
        """Execute complete outreach strategy for a job"""
        try:
            logger.info(f"Starting outreach strategy for {job_info['title']} at {job_info['company']}")
            
            # Find hiring managers
            hiring_managers = self.find_hiring_managers(job_info['company'], job_info['title'])
            
            if not hiring_managers:
                logger.info(f"No hiring managers found for {job_info['company']}")
                return {'success': False, 'reason': 'No hiring managers found'}
            
            # Send connection requests
            connections_sent = 0
            for person in hiring_managers[:3]:  # Limit to top 3
                if random.random() < self.config['outreach']['connection_request_probability']:
                    if self.send_connection_request(person, job_info):
                        connections_sent += 1
                        time.sleep(random.uniform(5, 10))  # Delay between requests
            
            # Schedule follow-up messages
            if connections_sent > 0:
                logger.info(f"Scheduled {connections_sent} follow-up messages for later")
                # In a real implementation, you'd schedule these for later
            
            return {
                'success': True,
                'connections_sent': connections_sent,
                'hiring_managers_found': len(hiring_managers)
            }
            
        except Exception as e:
            logger.error(f"Outreach strategy failed: {e}")
            return {'success': False, 'reason': str(e)}
    
    def get_outreach_summary(self) -> Dict:
        """Get summary of outreach activities"""
        return {
            'connections_sent': len(self.connections_sent),
            'messages_sent': len(self.messages_sent),
            'total_outreach': len(self.connections_sent) + len(self.messages_sent),
            'connections': self.connections_sent,
            'messages': self.messages_sent
        }