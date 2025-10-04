import requests

def test_api():
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Base URL
    base_url = 'http://127.0.0.1:8000'
    
    print("1. Testing CSRF endpoint...")
    response = session.get(f'{base_url}/api/csrf/')
    if response.status_code == 200:
        print("✓ CSRF endpoint working")
        csrf_token = response.json().get('csrfToken')
        print(f"CSRF Token: {csrf_token}")
    else:
        print(f"✗ CSRF endpoint failed: {response.status_code}")
        return
    
    print("\n2. Testing login...")
    login_data = {
        'username': 'fintech',
        'password': 'hackathon'
    }
    headers = {
        'X-Csrftoken': csrf_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    response = session.post(
        f'{base_url}/api/login/',
        json=login_data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n3. Testing create savings group...")
        group_data = {
            'name': 'Test Women Savings Group',
            'risk_tolerance': 'LOW',
            'tier_level': 1
        }
        response = session.post(
            f'{base_url}/api/savings-groups/',
            json=group_data,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            group_id = response.json()['id']
            
            print("\n4. Testing create financial education...")
            education_data = {
                'title': 'Understanding Interest Rates',
                'content': 'Learn about how interest rates affect your savings and loans.',
                'difficulty_level': 'BASIC',
                'points': 100
            }
            response = session.post(
                f'{base_url}/api/education/',
                json=education_data,
                headers=headers
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            print("\n5. Testing create investment...")
            investment_data = {
                'group': group_id,
                'investment_type': 'UNIT_TRUST',
                'amount': '1000.00',
                'current_value': '1000.00',
                'provider': 'Stanbic'
            }
            response = session.post(
                f'{base_url}/api/investments/',
                json=investment_data,
                headers=headers
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    
    print("\n6. Testing logout...")
    response = session.post(
        f'{base_url}/api/logout/',
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == '__main__':
    test_api()
