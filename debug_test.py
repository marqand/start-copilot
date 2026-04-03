#!/usr/bin/env python3
"""
Debug script to test FastAPI functionality manually
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fastapi.testclient import TestClient
    from app import app, get_activities

    print("✓ Imports successful")

    # Test the activities function
    activities = get_activities()
    print(f"✓ get_activities() returned {len(activities)} activities")

    # Test the test client
    client = TestClient(app)
    response = client.get('/activities')

    print(f"✓ GET /activities status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Response contains {len(data)} activities")
        print(f"✓ Activity names: {list(data.keys())}")

        # Check Chess Club
        if "Chess Club" in data:
            chess_club = data["Chess Club"]
            participants = chess_club.get("participants", [])
            print(f"✓ Chess Club has {len(participants)} participants: {participants}")
        else:
            print("✗ Chess Club not found in response")
    else:
        print(f"✗ Error response: {response.text}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()