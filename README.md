# LinkedIn Job Application Automation Agent

An intelligent, human-like LinkedIn job application automation system that automatically applies to data engineering, AI, and BI roles in Singapore and Hong Kong.

## 🚀 Features

- **Intelligent Job Matching**: Automatically identifies and applies to relevant roles
- **Customized Resumes**: AI-generated resumes tailored to each specific job
- **Personalized Cover Letters**: Heartfelt, genuine cover letters for each application
- **Hiring Manager Outreach**: Connects with and messages hiring managers
- **Anti-Detection**: Human-like behavior to avoid LinkedIn bot detection
- **Smart Scheduling**: Takes breaks and operates at human pace

## 🎯 Target Roles

- Data Engineer
- Data Analyst
- AI Engineer
- Business Intelligence Developer
- AI Prototyper

## 📍 Target Locations

- **Primary**: Singapore
- **Secondary**: Hong Kong

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Chrome browser
- OpenAI API key
- LinkedIn account

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linkedin-job-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome WebDriver**
   ```bash
   # The system uses undetected-chromedriver which should auto-install
   # If you encounter issues, install manually:
   pip install webdriver-manager
   ```

4. **Configure your profile**
   - Edit `profile.md` with your information
   - Fill in all sections with your actual skills and experience
   - Add your personal notes for cover letters

5. **Set up configuration**
   - Edit `config.yaml` with your LinkedIn credentials
   - Add your OpenAI API key
   - Customize job search parameters

6. **Set environment variables**
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

## 📝 Profile Setup

Edit `profile.md` with your information:

```markdown
## Personal Information
- **Name**: [Your Actual Name]
- **Location**: Singapore
- **Current Role**: [Your Current Position]
- **Years of Experience**: [X] years

## Core Skills & Technologies
### Data Engineering
- **Databases**: PostgreSQL, MySQL, MongoDB
- **Big Data**: Hadoop, Spark, Kafka
- **ETL/ELT**: Apache NiFi, Airflow
- **Cloud Platforms**: AWS, Azure, GCP

## Professional Experience
### [Company Name] - [Position] (YYYY-YYYY)
- **Key Achievements**:
  - [Specific achievement with metrics]
- **Technologies Used**: [List relevant tech]
- **Impact**: [Quantified results]

## Personal Notes for Cover Letters
### Why I'm Looking for New Opportunities
[Share your genuine reasons - career growth, new challenges, etc.]
```

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
linkedin:
  email: "your_email@example.com"
  password: "your_password"
  headless: false  # Set to true for headless mode

openai_api_key: "your_openai_api_key_here"

job_search:
  keywords:
    - "data engineer"
    - "data analyst"
    - "ai engineer"
  locations:
    - "Singapore"
    - "Hong Kong"
  max_applications_per_session: 50
```

## 🚀 Usage

### Run the Complete Automation

```bash
python linkedin_job_agent.py
```

### Generate Individual Resumes

```bash
python resume_generator.py "Data Engineer" "Google"
python resume_generator.py "AI Engineer" "Microsoft" "my_resume.txt"
```

### Test Resume Generation

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your_key_here"

# Generate a resume for a specific role
python resume_generator.py "Business Intelligence Developer" "Shopee"
```

## 🔧 How It Works

### 1. Job Discovery
- Searches LinkedIn for relevant positions
- Filters by location and role type
- Scores jobs by relevance

### 2. Resume Customization
- Analyzes job requirements
- Identifies relevant skills from your profile
- Generates tailored resume using AI
- Focuses on transferable skills

### 3. Cover Letter Generation
- Creates personalized, heartfelt letters
- References specific company and role
- Incorporates your personal story
- Maintains authenticity

### 4. Application Process
- Fills out application forms
- Uploads customized materials
- Submits applications
- Records results

### 5. Hiring Manager Outreach
- Identifies relevant contacts
- Sends personalized connection requests
- Follows up with messages
- Builds professional relationships

## 🛡️ Anti-Detection Features

- **Human-like Delays**: Random delays between actions
- **Natural Typing**: Human-like text input patterns
- **Random Breaks**: Takes breaks to appear human
- **User Agent Rotation**: Varies browser signatures
- **Session Management**: Limits applications per session
- **Behavioral Patterns**: Mimics human browsing habits

## 📊 Monitoring & Logging

The system provides comprehensive logging:

- **Application tracking**: Records all applications
- **Success rates**: Monitors application success
- **Session summaries**: Detailed session reports
- **Error logging**: Tracks and reports issues

Logs are saved to `linkedin_agent.log` and session results to JSON files.

## ⚠️ Important Notes

### LinkedIn Terms of Service
- This tool automates LinkedIn interactions
- Use responsibly and within LinkedIn's terms
- Consider LinkedIn Premium for better results
- Respect rate limits and human behavior

### Ethical Considerations
- Only apply to roles you're genuinely interested in
- Ensure your profile information is accurate
- Don't spam or abuse the system
- Use for legitimate job searching purposes

### Risk Mitigation
- Start with small application batches
- Monitor for any account restrictions
- Use human-like timing patterns
- Take regular breaks between sessions

## 🔍 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   ```bash
   pip install --upgrade undetected-chromedriver
   ```

2. **LinkedIn Login Problems**
   - Check credentials in config.yaml
   - Ensure 2FA is properly configured
   - Try logging in manually first

3. **OpenAI API Errors**
   - Verify API key is correct
   - Check API usage limits
   - Ensure sufficient credits

4. **Element Not Found Errors**
   - LinkedIn may have updated their interface
   - Check CSS selectors in the code
   - Update selectors if needed

### Debug Mode

Enable detailed logging by modifying the logging level in `config.yaml`:

```yaml
logging:
  level: "DEBUG"
```

## 📈 Performance Optimization

### Speed vs. Safety
- **Conservative**: 3-8 second delays (safer)
- **Moderate**: 2-5 second delays (balanced)
- **Aggressive**: 1-3 second delays (faster, riskier)

### Session Limits
- **Small**: 10-20 applications per session
- **Medium**: 20-50 applications per session
- **Large**: 50+ applications per session (not recommended)

## 🔄 Regular Maintenance

### Weekly Tasks
- Review application success rates
- Update profile with new skills/experience
- Check for LinkedIn interface changes
- Monitor account status

### Monthly Tasks
- Analyze hiring manager response rates
- Update target companies and roles
- Review and refine outreach strategies
- Backup application data

## 📚 Advanced Features

### Custom Job Filters
Add custom filters in `config.yaml`:

```yaml
job_search:
  custom_filters:
    company_size: ["startup", "scale-up"]
    industry: ["tech", "fintech", "healthcare"]
    remote_work: true
```

### Automated Follow-ups
Schedule follow-up messages:

```yaml
outreach:
  follow_up_schedule:
    - delay_hours: 24
      message_type: "thank_you"
    - delay_hours: 72
      message_type: "check_in"
```

### Integration with ATS
Parse job descriptions for better matching:

```yaml
resume_customization:
  parse_job_descriptions: true
  keyword_matching: true
  skill_extraction: true
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational and personal use. Please respect LinkedIn's terms of service and use responsibly.

## ⚖️ Disclaimer

This tool is provided as-is for educational purposes. Users are responsible for:

- Compliance with LinkedIn's terms of service
- Ethical use of automation tools
- Accuracy of their profile information
- Consequences of their actions

The developers are not responsible for any account restrictions or other consequences of using this tool.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the logs for error details
3. Check GitHub issues for similar problems
4. Create a new issue with detailed information

---

**Happy job hunting! 🎯✨**
