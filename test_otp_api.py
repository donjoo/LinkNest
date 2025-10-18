#!/usr/bin/env python3
"""
Test script for OTP API endpoints
Run this script to test the OTP functionality
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8001/api/auth"

def test_registration():
    """Test user registration"""
    print("Testing user registration...")
    
    # Test data
    import time
    timestamp = int(time.time())
    user_data = {
        "email": f"test{timestamp}@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpassword123",
        "password_confirm": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/register/", json=user_data)
    print(f"Registration Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return user_data["email"]
    return None

def test_otp_status(email):
    """Test OTP status endpoint"""
    print(f"\nTesting OTP status for {email}...")
    
    response = requests.get(f"{BASE_URL}/otp-status/?email={email}")
    print(f"OTP Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_resend_otp(email):
    """Test OTP resend"""
    print(f"\nTesting OTP resend for {email}...")
    
    response = requests.post(f"{BASE_URL}/resend-otp/", json={"email": email})
    print(f"Resend Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_verify_otp(email, code):
    """Test OTP verification"""
    print(f"\nTesting OTP verification for {email} with code {code}...")
    
    response = requests.post(f"{BASE_URL}/verify-otp/", json={
        "email": email,
        "code": code
    })
    print(f"Verification Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def main():
    """Main test function"""
    print("OTP API Test Script")
    print("=" * 50)
    
    # Test registration
    email = test_registration()
    if not email:
        print("Registration failed. Exiting.")
        return
    
    # Test OTP status
    test_otp_status(email)
    
    # Test resend OTP
    test_resend_otp(email)
    
    # Test OTP status again
    test_otp_status(email)
    
    # Get OTP code from user
    print(f"\nPlease check the email for {email} and enter the 6-digit OTP code:")
    otp_code = input("Enter OTP code: ").strip()
    
    if len(otp_code) == 6 and otp_code.isdigit():
        # Test verification
        success = test_verify_otp(email, otp_code)
        if success:
            print("\n✅ OTP verification successful!")
        else:
            print("\n❌ OTP verification failed!")
    else:
        print("\n❌ Invalid OTP code format!")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
