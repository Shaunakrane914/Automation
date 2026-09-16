# CONFIGURATION TEMPLATE - LinkedIn Credentials
# Copy this to config/secrets.py and fill in your details

'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

version:    24.12.29.12.30
'''


###################################################### CONFIGURE YOUR CREDENTIALS HERE ######################################################

# LinkedIn Login Credentials
# If left empty (""), the bot will try to use your saved Chrome profile
# If that fails, it will ask you to login manually
username = "your.email@example.com"             # Your LinkedIn email
password = "your_password_here"                 # Your LinkedIn password

# AI Integration (Optional - for resume customization and intelligent question answering)
use_AI = False                                  # Set to True if you want to use AI features

# Which AI provider do you want to use?
ai_provider = "openai"                          # Options: "openai", "gemini", "deepseek"

# OpenAI API Key (Get from: https://platform.openai.com/api-keys)
openai_api_key = ""                             # Example: "sk-proj-abc123..."

# Gemini API Key (Get from: https://makersuite.google.com/app/apikey)
gemini_api_key = ""                             # Example: "AIza..."

# DeepSeek API Key (Get from: https://platform.deepseek.com/)
deepseek_api_key = ""                           # Example: "sk-..."


############################################################################################################
'''
SECURITY NOTE:
- Never share your credentials or API keys
- This file is in .gitignore to prevent accidental commits
- Keep your API keys secure

THANK YOU for using my tool 😊! Wishing you the best in your job hunt 🙌🏻!

Gratefully yours 🙏🏻,
Sai Vignesh Golla
'''
############################################################################################################
