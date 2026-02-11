import requests
import json

try:
    # Test register endpoint
    url = 'http://127.0.0.1:8000/auth/register'
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    response = requests.post(url, json=data)
    print('Register Status Code:', response.status_code)
    print('Register Response Headers:', response.headers)
    print('Register Response Body:', response.text)
    
except Exception as e:
    print('Error:', str(e))
