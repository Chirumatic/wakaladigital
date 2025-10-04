import requests
import json
import sys
import time
from requests.exceptions import RequestException

BASE_URL = 'http://127.0.0.1:8000'

def wait_for_server(max_retries=5):
    for i in range(max_retries):
        try:
            response = requests.get(BASE_URL)
            if response.status_code == 200:
                return True
        except RequestException:
            print(f"Waiting for server to start (attempt {i+1}/{max_retries})...")
            time.sleep(2)
    return False
session = requests.Session()

def test_csrf():
    # Get CSRF token
    response = session.get(f'{BASE_URL}/api/csrf/', headers={'Accept': 'application/json'})
    print('\n1. Testing CSRF Token Endpoint:')
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.json()}')
    
    # Get both the CSRF token from the cookie and the response
    csrf_token = response.cookies.get('csrftoken')
    if not csrf_token:
        csrf_token = response.json().get('csrfToken')
    
    session.headers.update({
        'X-CSRFToken': csrf_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    return csrf_token

def test_login(csrf_token):
    # Test login
    headers = {'X-CSRFToken': csrf_token}
    data = {
        'username': 'fintech',
        'password': 'hackathon'
    }
    response = session.post(
        f'{BASE_URL}/api/login/',
        json=data,
        headers=headers
    )
    print('\n2. Testing Login Endpoint:')
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.json()}')
    return response.status_code == 200

def test_savings_group(csrf_token):
    # Test creating a savings group
    headers = {'X-CSRFToken': csrf_token}
    data = {
        'name': 'Test Women Savings Group',
        'risk_tolerance': 'LOW',
        'tier_level': 1
    }
    response = session.post(
        f'{BASE_URL}/api/savings-groups/',
        json=data,
        headers=headers
    )
    print('\n3. Testing Create Savings Group Endpoint:')
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.json() if response.status_code == 201 else response.text}')
    return response.status_code == 201

def test_financial_education(csrf_token):
    # Test creating financial education content
    headers = {'X-CSRFToken': csrf_token}
    data = {
        'title': 'Understanding Interest Rates',
        'content': 'Learn about how interest rates affect your savings and loans.',
        'difficulty_level': 'BASIC',
        'points': 100
    }
    response = session.post(
        f'{BASE_URL}/api/education/',
        json=data,
        headers=headers
    )
    print('\n4. Testing Create Financial Education Endpoint:')
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.json() if response.status_code == 201 else response.text}')
    return response.status_code == 201

def test_investment(csrf_token, group_id):
    # Test creating an investment
    headers = {'X-CSRFToken': csrf_token}
    data = {
        'group': group_id,
        'investment_type': 'UNIT_TRUST',
        'amount': '1000.00',
        'current_value': '1000.00',
        'provider': 'Stanbic'
    }
    response = session.post(
        f'{BASE_URL}/api/investments/',
        json=data,
        headers=headers
    )
    print('\n5. Testing Create Investment Endpoint:')
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.json() if response.status_code == 201 else response.text}')
    return response.status_code == 201

def test_logout(csrf_token):
    # Test logout
    headers = {'X-CSRFToken': csrf_token}
    response = session.post(
        f'{BASE_URL}/api/logout/',
        headers=headers
    )
    print('\n6. Testing Logout Endpoint:')
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.json()}')
    return response.status_code == 200

def main():
    print("Starting API Tests...")
    
    # Wait for server to be ready
    if not wait_for_server():
        print("Error: Could not connect to the server. Please ensure it's running.")
        sys.exit(1)

    try:
        # Get CSRF token
        csrf_token = test_csrf()
        
        # Test login
        if test_login(csrf_token):
            print("\n✓ Login successful!")
            
            # Test creating a savings group
            if test_savings_group(csrf_token):
                print("✓ Savings group created successfully!")
                
                # Get the first savings group ID for investment test
                response = session.get(f'{BASE_URL}/api/savings-groups/')
                group_id = response.json()['results'][0]['id']
                
                # Test creating financial education content
                if test_financial_education(csrf_token):
                    print("✓ Financial education content created successfully!")
                
                # Test creating an investment
                if test_investment(csrf_token, group_id):
                    print("✓ Investment created successfully!")
            
            # Test logout
            if test_logout(csrf_token):
                print("✓ Logout successful!")
        
        print("\nAPI Tests completed!")
    except RequestException as e:
        print(f"\nError during API test: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)
        print("\n✓ Login successful!")
        
        # Test creating a savings group
        if test_savings_group(csrf_token):
            print("✓ Savings group created successfully!")
            
            # Get the first savings group ID for investment test
            response = session.get(f'{BASE_URL}/api/savings-groups/')
            group_id = response.json()['results'][0]['id']
            
            # Test creating financial education content
            if test_financial_education(csrf_token):
                print("✓ Financial education content created successfully!")
            
            # Test creating an investment
            if test_investment(csrf_token, group_id):
                print("✓ Investment created successfully!")
        
        # Test logout
        if test_logout(csrf_token):
            print("✓ Logout successful!")
    
    print("\nAPI Tests completed!")

if __name__ == '__main__':
    main()
