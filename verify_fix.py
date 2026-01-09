
from app import app
from flask import session

def test_analysis():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user'] = {'info_username': 'student', 'roll_number': '1001'}
        
        # Access analysis page
        response = client.get('/analysis')
        
        if response.status_code == 200:
            print("SUCCESS: Analysis page loaded successfully.")
        else:
            print(f"FAILURE: Status code {response.status_code}")
            try:
                print(response.data.decode())
            except:
                pass

if __name__ == "__main__":
    test_analysis()
