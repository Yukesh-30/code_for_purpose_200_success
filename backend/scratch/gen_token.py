import sys
import os

# Add the current directory to sys.path to import from services
sys.path.append(os.getcwd())

from services.auth_service import generate_token

# Dummy user data
user_id = 1
role = 'msme_owner'

token = generate_token(user_id, role)
print(token)
